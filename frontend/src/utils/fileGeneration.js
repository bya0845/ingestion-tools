export const triggerBrowserDownload = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  console.log("File download completed");
};

export const selectOutputDirectory = async () => {
  try {
    const dirHandle = await window.showDirectoryPicker();
    return { dirHandle, dirName: dirHandle.name || "" };
  } catch (err) {
    if (err.name === "AbortError") {
      console.log("Directory selection cancelled by user");
      return null;
    }
    throw err;
  }
};

export const saveFileToDirectory = async (blob, filename, dirHandle) => {
  const fileHandle = await dirHandle.getFileHandle(filename, {
    create: true,
  });
  const writable = await fileHandle.createWritable();
  await writable.write(blob);
  await writable.close();
};
