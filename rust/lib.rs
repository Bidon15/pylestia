mod types;

use pyo3::prelude::*;

#[pymodule]
fn pylestia_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    types::register_module(m)?;
    Ok(())
}
