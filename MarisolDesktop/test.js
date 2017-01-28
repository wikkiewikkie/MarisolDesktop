function convertDataURIToBinary(dataURI) {
  var raw = window.atob(dataURI);
  var rawLength = raw.length;
  var array = new Uint8Array(new ArrayBuffer(rawLength));

  for(var i = 0; i < rawLength; i++) {
    array[i] = raw.charCodeAt(i);
  }
  return array;
}

function qpdf_ShowPdfFile(b64Data) {
    var blob = convertDataURIToBinary(b64Data);
    console.log(blob);
    PDFJS.getDocument({data: blob}).then(function getPdfHelloWorld(pdf) {
    // Fetch the first page.
    pdf.getPage(1).then(function getPageHelloWorld(page) {
      var scale = 1.5;
      var viewport = page.getViewport(scale);
      // Prepare canvas using PDF page dimensions.
      var canvas = document.getElementById('the-canvas');
      var context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      // Render PDF page into canvas context.
      var renderContext = {
        canvasContext: context,
        viewport: viewport
      };
      page.render(renderContext);
    });
});
}

// In production, the bundled pdf.js shall be used instead of RequireJS.
$(document).ready( function() {
  // In production, change this to point to the built `pdf.worker.js` file.
  PDFJS.workerSrc = 'pdf.worker.js';
  PDFJS.disableWorker = true;
});