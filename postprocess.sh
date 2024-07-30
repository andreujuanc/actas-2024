cp actas_raw/** actas
cd actas
for file in *.jpg; do
  if [ -f "$file" ]; then
    echo "Processing $file"
    jpegoptim --size=85k $file
  fi
done

cd ..