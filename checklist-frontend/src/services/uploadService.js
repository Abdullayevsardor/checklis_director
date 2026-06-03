import api from "../api/axios";

export async function uploadPhotoFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post("/uploads", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return res.data;
}