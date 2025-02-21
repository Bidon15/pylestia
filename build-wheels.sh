#!/bin/bash
set -ex

dnf -y install protobuf protobuf-compiler protobuf-devel
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"

# Compile wheels
for PYBIN in /opt/python/cp{310,311,312,313}*/bin; do
    if [[ $PYBIN == *"313t"* ]]; then
      echo "Skipping experimental Python 3.13t"
      continue
    fi
    rm -rf /io/build/
    "${PYBIN}/pip" install -U setuptools setuptools-rust wheel
    "${PYBIN}/pip" wheel /io/ -w /io/dist/ --no-deps
done

# Bundle external shared libraries into the wheels
for whl in /io/dist/*{310,311,312,313}*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done

# cleanup
for whl in /io/dist/*{310,311,312,313}-linux_x86_64.whl; do
  rm "$whl"
done
