import { useAuth } from "@clerk/clerk-react";

export function useExport() {
  const { getToken } = useAuth();

  const descargarReporte = async (verificacionId, formato) => {
    try {
      const token = await getToken();

      const response = await fetch(
        `http://localhost:8000/api/reportes/descargar/${verificacionId}?formato=${formato}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      // Obtener el blob
      const blob = await response.blob();

      // Crear URL temporal y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      
      // Obtener nombre del archivo del header
      const contentDisposition = response.headers.get("content-disposition");
      let filename = `analisis.${formato}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/"/g, "");
        }
      }

      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      return { success: true, filename };
    } catch (error) {
      console.error("Error descargando reporte:", error);
      return { success: false, error: error.message };
    }
  };

  return { descargarReporte };
}
