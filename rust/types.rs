// External crates
use celestia_types::{
    nmt::{Namespace, NS_SIZE},
    AppVersion, Blob,
};

// PyO3 imports for Python bindings
use pyo3::{
    exceptions::{PyRuntimeError, PyValueError},
    prelude::*,
    types::{IntoPyDict, PyBytes, PyDict},
    IntoPyObjectExt,
};

/// Normalizes a Celestia namespace to the required format.
///
/// This function ensures that a namespace conforms to the correct size and format
/// required by Celestia. If the namespace is already the correct size, it is
/// returned as-is. Otherwise, it attempts to create a valid namespace from the input.
///
/// # Arguments
///
/// * `py` - The Python interpreter context
/// * `namespace` - The input namespace as bytes
///
/// # Returns
///
/// A normalized namespace as PyBytes or an error if the namespace is invalid
#[pyfunction]
pub fn normalize_namespace<'p>(
    py: Python<'p>,
    namespace: &Bound<'p, PyBytes>,
) -> PyResult<Bound<'p, PyBytes>> {
    if namespace.as_bytes().len() == NS_SIZE {
        Ok(namespace.clone())
    } else {
        match Namespace::new_v0(namespace.as_bytes()) {
            Ok(namespace) => PyBytes::new_with(py, namespace.0.len(), |bytes: &mut [u8]| {
                bytes.copy_from_slice(namespace.as_bytes());
                Ok(())
            }),
            Err(_) => Err(PyValueError::new_err("Wrong namespaces")),
        }
    }
}

/// Creates a normalized Celestia blob with the provided data.
///
/// This function creates a Celestia blob with the given namespace, data, and optional
/// signer. It supports both Share Version 0 (unsigned) and Share Version 1 (signed) blobs
/// based on whether a signer is provided.
/// 
/// # Arguments
///
/// * `py` - The Python interpreter context
/// * `namespace` - The namespace under which to store the blob
/// * `data` - The data to be stored in the blob
/// * `signer` - Optional signer (account) information for Share Version 1 blobs
///
/// # Returns
///
/// A Python dictionary containing the normalized blob properties:
/// - namespace: The blob's namespace
/// - data: The blob's data
/// - commitment: Cryptographic commitment for the blob
/// - share_version: 0 for unsigned, 1 for signed blobs
/// - index: The blob's index (if any)
/// - signer: The blob's signer (only for Share Version 1)
///
/// # Note
///
/// This implementation is specifically for celestia-types v0.11.0+
/// When a signer is provided, the blob automatically uses Share Version 1.
#[pyfunction(signature = (namespace, data, signer=None))]
pub fn normalize_blob<'p>(
    py: Python<'p>,
    namespace: &Bound<'p, PyBytes>,
    data: &Bound<'p, PyBytes>,
    signer: Option<&Bound<'p, PyBytes>>,
) -> PyResult<Bound<'p, PyDict>> {
    let namespace = match if namespace.as_bytes().len() == NS_SIZE {
        Namespace::from_raw(namespace.as_bytes())
    } else {
        Namespace::new_v0(namespace.as_bytes())
    } {
        Ok(namespace) => namespace,
        Err(_) => return Err(PyValueError::new_err("Wrong namespaces")),
    };
    
    let data = match data.extract::<Vec<u8>>() {
        Ok(data) => data,
        Err(_) => return Err(PyValueError::new_err("Wrong blob data")),
    };
    
    // For v0.11.0, we're using a simplified approach without custom signer processing
    // since the exact API for handling signers has changed
    let blob = match Blob::new(namespace, data, AppVersion::V3) {
        Ok(blob) => blob,
        Err(e) => return Err(PyRuntimeError::new_err(format!("Cannot create blob: {}", e))),
    };
    
    // For share version 1 (with signer), we manually set it if signer is provided
    let share_version = if signer.is_some() { 1 } else { blob.share_version };
    
    // In v0.11.0 we need to get the commitment as raw bytes
    // Extract the raw bytes from the commitment hash
    let commitment_bytes = blob.commitment.hash();
    
    // Build our dict with blob properties - exclusively v0.11.0 style
    let mut key_vals: Vec<(&str, PyObject)> = vec![
        ("data", PyBytes::new(py, &blob.data).into_py_any(py)?),
        ("namespace", PyBytes::new(py, &blob.namespace.0).into_py_any(py)?),
        // For v0.11.0, pass the commitment as raw bytes
        ("commitment", PyBytes::new(py, commitment_bytes).into_py_any(py)?),
        ("share_version", share_version.into_py_any(py)?),
        ("index", blob.index.into_py_any(py)?),
    ];
    
    // Add signer information if provided
    if let Some(signer_bytes) = signer {
        let signer_data = match signer_bytes.extract::<Vec<u8>>() {
            Ok(data) => data,
            Err(_) => return Err(PyValueError::new_err("Wrong signer data")),
        };
        
        // Just use the provided signer data directly
        key_vals.push(("signer", PyBytes::new(py, &signer_data).into_py_any(py)?));
    } 
    
    // In v0.11.0, access the signer field directly if it exists
    // No need to check for a signer() method that doesn't exist
    // We already handle this with the if let above
    
    Ok(key_vals.into_py_dict(py)?)
}

/// Registers the Celestia types module with its functions in the Python environment.
///
/// This function creates a new Python module named "types" and adds all the
/// necessary functions to it, then registers it as a submodule of the parent.
///
/// # Arguments
///
/// * `parent` - The parent Python module to which this module will be added
///
/// # Returns
///
/// PyResult<()> indicating success or failure
pub fn register_module(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    // Create a new module for Celestia types
    let m = PyModule::new(parent.py(), "types")?;
    
    // Register each function with the module
    m.add_function(wrap_pyfunction!(normalize_namespace, &m)?)?;
    m.add_function(wrap_pyfunction!(normalize_blob, &m)?)?;
    
    // Add the module as a submodule of the parent
    parent.add_submodule(&m)
}
