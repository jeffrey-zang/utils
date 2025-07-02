(function () {
  const keep = document.getElementById("pdf_document_scroll_container");
  if (!keep) return;

  setTimeout(() => {
    const body = document.body;
    const clone = keep.cloneNode(true);

    body.innerHTML = "";
    body.appendChild(clone);

    // Inject print-friendly CSS
    const style = document.createElement("style");
    style.textContent = `
    @media print {
      body {
        margin: 0;
        padding: 0;
        -webkit-print-color-adjust: exact;
      }
      * {
        page-break-inside: avoid !important;
        overflow: visible !important;
      }
      button {
        display: none !important;
      }
    }
  `;
    document.head.appendChild(style);

    // Create print button
    const printBtn = document.createElement("button");
    printBtn.textContent = "Save as PDF";
    printBtn.style.position = "fixed";
    printBtn.style.top = "20px";
    printBtn.style.right = "20px";
    printBtn.style.zIndex = "9999";
    printBtn.style.padding = "10px 16px";
    printBtn.style.backgroundColor = "#007bff";
    printBtn.style.color = "white";
    printBtn.style.border = "none";
    printBtn.style.borderRadius = "4px";
    printBtn.style.cursor = "pointer";
    printBtn.onclick = () => window.print();

    body.appendChild(printBtn);
  }, 15000);
})();
