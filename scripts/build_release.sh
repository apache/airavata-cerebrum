#!/bin/bash
print_usage() {
  echo "USAGE:: $0 -r RELEASE [-b BUILD_DIR]"
  exit 0
}

BUILD_DIR=build
while getopts "r:b:hu" opt; do
  case $opt in
  r) RELEASE=$OPTARG ;;
  b) BUILD_DIR=$OPTARG ;;
  h) print_usage ;;
  u) UPLOAD='Y' ;;
  *)
    echo "Invalid argument"
    exit 1
    ;;
  esac
done

if [ -z "$RELEASE" ]; then
  echo "Release name not provided; Run with -r"
  print_usage
fi

rm -rf "$BUILD_DIR"
python3 -m build -o "$BUILD_DIR/dist"
if [ -z ${UPLOAD+x} ]; then
  echo "Skipping uploading to PYPI"
else
  echo "Uploading to PYPI"
  python3 -m twine upload --repository pypi $BUILD_DIR/dist/* --verbose
fi
mkdir -p "$BUILD_DIR/examples"
tar cvzf $BUILD_DIR/airavata-cerebrum-$RELEASE-examples.tar.gz examples/
