import { useState } from "react";
import {
  triggerBrowserDownload,
  selectOutputDirectory,
  saveFileToDirectory,
} from "../utils/fileGeneration";

export const useFileGeneration = (pageName = "Page") => {
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [outputDir, setOutputDir] = useState("");
  const [useDefaultDownload, setUseDefaultDownload] = useState(true);

  const createGenerateHandler =
    (documentType, apiFunction, dataValidator) => async (e) => {
      e.preventDefault();
      console.log(`${pageName}: Generate ${documentType} button clicked`);

      const validation = dataValidator();
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      let trimmedDir = outputDir;
      let dirHandle = null;

      if (!useDefaultDownload && !outputDir) {
        try {
          const result = await selectOutputDirectory();
          if (result === null) return;
          dirHandle = result.dirHandle;
          trimmedDir = result.dirName;
        } catch (err) {
          setError(
            "Failed to select directory. Falling back to browser download.",
          );
          trimmedDir = "";
        }
      }

      console.log(`${pageName}: Generating ${documentType} with:`, {
        outputDir: trimmedDir,
      });
      setOutputDir(trimmedDir);
      setLoading(true);
      setError(null);
      setSuccessMessage(null);

      try {
        console.log(`${pageName}: Calling ${documentType} API...`);
        const { blob, filename } = await apiFunction(trimmedDir);
        console.log(`${pageName}: ${documentType} generated successfully`, {
          filename,
        });

        if (useDefaultDownload) {
          triggerBrowserDownload(blob, filename);
          setSuccessMessage(
            `Download complete, saved to default browser download folder as "${filename}"`,
          );
        } else if (dirHandle) {
          try {
            await saveFileToDirectory(blob, filename, dirHandle);
            console.log(`${pageName}: File saved to directory`, filename);
            setSuccessMessage(
              `Download complete, saved to output: ${dirHandle.name}/${filename}`,
            );
          } catch (err) {
            console.error(
              `${pageName}: Failed to write file to directory`,
              err,
            );
            setError("Failed to save file to directory. Downloading instead.");
            triggerBrowserDownload(blob, filename);
          }
        } else {
          console.log(`${pageName}: File saved to server directory`, filename);
          setSuccessMessage(`Saved to ${trimmedDir}/${filename}`);
        }
      } catch (err) {
        console.error(`${pageName}: ${documentType} generate error`, err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

  return {
    error,
    setError,
    successMessage,
    setSuccessMessage,
    loading,
    setLoading,
    outputDir,
    setOutputDir,
    useDefaultDownload,
    setUseDefaultDownload,
    createGenerateHandler,
  };
};
