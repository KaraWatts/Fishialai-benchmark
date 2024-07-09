import { useState } from "react";

export function Upload() {
  const [data, setData] = useState(null);
  const [images, setImages] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const handleChange = e => {
    const fileReader = new FileReader();
    fileReader.readAsText(e.target.files[0], "UTF-8");
    fileReader.onload = e => {
      console.log("Raw file content:", e.target.result); // Debugging: Log raw file content
      try {
        const json = JSON.parse(e.target.result);
        setData(json); // Save dataset info
        setImages(json.image); // Save all images
        console.log("Parsed JSON Info:", json.info);
      } catch (err) {
        console.error("Error Parsing JSON:", err);
        setData({ error: "Invalid JSON" });
      }
    };
  };

  const handleImageClick = (image) => {
    setSelectedImage(image)
    
  }

  return (
    <>
      <h1>Upload JSON file</h1>
      <input type="file" onChange={handleChange} accept=".json" />
      <br />
      {data && (
        <div>
        <pre>{JSON.stringify(data.info, null, 2)}</pre>
      {selectedImage && (
        <div>
          <h4>Selected Image Details:</h4>
          <p>Image ID: {selectedImage.id}</p>
          <p>Scientific Name: {selectedImage.scientific_name}</p>
          {/* Add more details as needed */}
        </div>
      )}
        <h4>Images List:</h4>
          <ul>
            {images.map((image) => (
              <li key={image.id} onClick={() => handleImageClick(image)} style={{ cursor: "pointer" }}>
                {image.coco_url} - Scientific Name: {image.scientific_name}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data && data.error && (
        <p>{data.error}</p>
      )}

      
    </>
  );
}
