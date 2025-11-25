// popup.js
// Reads date range from the popup and tells the Costco tab to start download.

const downloadBtn = document.getElementById("download");
const statusEl = document.getElementById("status");

function setStatus(message) {
    if (statusEl) {
        statusEl.textContent = message || "";
    }
}

downloadBtn.addEventListener("click", async () => {
    let start = document.getElementById("startDate").value;
    let end = document.getElementById("endDate").value;

    if (!start || !end) {
        alert("Please select both start and end dates.");
        return;
    }

    // Convert yyyy-mm-dd → mm/dd/yyyy (Costco API expects this)
    function format(d) {
        const [year, month, day] = d.split("-");
        return `${month}/${day}/${year}`;
    }

    start = format(start);
    end = format(end);

    setStatus("Finding active Costco tab…");

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.url || !tab.url.includes("costco.com")) {
        alert("Please open https://www.costco.com/myaccount/ordersandpurchases in a tab first, then run this extension.");
        setStatus("No active Costco tab detected.");
        return;
    }

    setStatus(`Starting download for ${start} → ${end}…`);
    downloadBtn.disabled = true;

    try {
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (start, end) => {
                document.dispatchEvent(
                    new CustomEvent("COSTCO_DOWNLOAD_RECEIPTS", {
                        detail: { start, end }
                    })
                );
            },
            args: [start, end]
        });

        // We can't know exactly when the JSON is saved from here,
        // but the content script will show an alert on success.
        setStatus("Download triggered. Check the Costco tab for progress.");
    } catch (err) {
        console.error("Error injecting script:", err);
        alert("Failed to trigger download in Costco tab:\n\n" + String(err));
        setStatus("Error starting download.");
    } finally {
        // Re-enable button so user can try again if needed
        downloadBtn.disabled = false;
    }
});