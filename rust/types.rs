use pyo3::prelude::*;

pub fn register_module(parent: &Bound<'_, PyModule>) -> PyResult<()> {
    let m = PyModule::new(parent.py(), "types")?;
    parent.add_submodule(&m)
}
