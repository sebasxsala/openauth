use quick_xml::events::{BytesRef, BytesText, Event};
use quick_xml::Reader;
use rustauth_core::error::RustAuthError;

pub fn validate_saml_xml(xml: &str) -> Result<(), RustAuthError> {
    let mut reader = Reader::from_str(xml);
    reader.config_mut().trim_text(true);
    let mut stack = Vec::new();

    loop {
        match reader.read_event() {
            Ok(Event::Start(element)) => stack.push(local_name(element.name().as_ref())?),
            Ok(Event::Empty(_)) => {}
            Ok(Event::End(element)) => {
                let name = local_name(element.name().as_ref())?;
                match stack.pop() {
                    Some(start) if start == name => {}
                    _ => {
                        return Err(RustAuthError::Api(
                            "Invalid SAML XML: mismatched closing element".to_owned(),
                        ));
                    }
                }
            }
            Ok(Event::DocType(_)) => {
                return Err(RustAuthError::Api(
                    "Invalid SAML XML: DOCTYPE is not allowed".to_owned(),
                ));
            }
            Ok(Event::Eof) => break,
            Err(error) => return Err(RustAuthError::Api(format!("Invalid SAML XML: {error}"))),
            Ok(_) => {}
        }
    }

    if !stack.is_empty() {
        return Err(RustAuthError::Api(
            "Invalid SAML XML: unexpected end of file".to_owned(),
        ));
    }

    Ok(())
}

pub fn local_name(name: &[u8]) -> Result<String, RustAuthError> {
    let value = std::str::from_utf8(name)
        .map_err(|error| RustAuthError::Api(format!("Invalid SAML XML name: {error}")))?;
    Ok(value
        .rsplit_once(':')
        .map_or(value, |(_, local)| local)
        .to_owned())
}

pub fn decode_xml_text(text: &BytesText<'_>) -> Result<String, RustAuthError> {
    text.decode()
        .map(|value| value.into_owned())
        .map_err(|error| RustAuthError::Api(error.to_string()))
}

pub fn decode_xml_reference(reference: &BytesRef<'_>) -> Result<String, RustAuthError> {
    if let Some(value) = reference
        .resolve_char_ref()
        .map_err(|error| RustAuthError::Api(error.to_string()))?
    {
        return Ok(value.to_string());
    }

    let name = reference
        .decode()
        .map_err(|error| RustAuthError::Api(error.to_string()))?;
    quick_xml::escape::resolve_predefined_entity(&name)
        .map(str::to_owned)
        .ok_or_else(|| RustAuthError::Api(format!("unrecognized XML entity `{name}`")))
}
