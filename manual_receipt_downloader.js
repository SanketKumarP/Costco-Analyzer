// ======================================================================
// Costco Receipt Downloader  (Warehouse + Gas)
// ----------------------------------------------------------------------
// HOW TO USE:
// 1. Open https://www.costco.com/myaccount/ordersandpurchases
// 2. Right-click → Inspect → Console
// 3. Change the data range in following code
// 3. Paste this entire script and press Enter
// 4. A JSON file with all receipts in the selected date range will download
// ======================================================================

// ---- SELECT DATE RANGE ----
// Format: "MM/DD/YYYY"
const FROM_DATE = "01/01/2023";
const TO_DATE   = "12/31/2025";

// ======================================================================
// 1. Fetch ALL Costco Receipts (Warehouse + Gas)
// ======================================================================

async function fetchReceipts(startDate, endDate) {
    console.log(`📡 Fetching receipts from ${startDate} → ${endDate} ...`);

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.responseType = "json";

        xhr.open("POST", "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql");

        // Required Costco API headers
        xhr.setRequestHeader("Content-Type", "application/json-patch+json");
        xhr.setRequestHeader("Costco.Env", "ecom");
        xhr.setRequestHeader("Costco.Service", "restOrders");
        xhr.setRequestHeader("Costco-X-Wcs-Clientid", localStorage.getItem("clientID"));
        xhr.setRequestHeader("Client-Identifier", "481b1aec-aa3b-454b-b81b-48187e28f205");
        xhr.setRequestHeader("Costco-X-Authorization", "Bearer " + localStorage.getItem("idToken"));

        // GraphQL query
        const payload = {
            query: `
                query receiptsWithCounts($startDate: String!, $endDate: String!) {
                  receiptsWithCounts(startDate: $startDate, endDate: $endDate) {
                    receipts {
                      warehouseName
                      receiptType
                      documentType
                      transactionDateTime
                      transactionDate
                      companyNumber
                      warehouseNumber
                      operatorNumber
                      warehouseShortName
                      registerNumber
                      transactionNumber
                      transactionType
                      transactionBarcode
                      total
                      warehouseAddress1
                      warehouseAddress2
                      warehouseCity
                      warehouseState
                      warehouseCountry
                      warehousePostalCode
                      totalItemCount
                      subTotal
                      taxes
                      invoiceNumber
                      sequenceNumber
                      itemArray {
                        itemNumber
                        itemDescription01
                        frenchItemDescription1
                        itemDescription02
                        frenchItemDescription2
                        itemIdentifier
                        itemDepartmentNumber
                        unit
                        amount
                        taxFlag
                        merchantID
                        entryMethod
                        transDepartmentNumber
                        fuelUnitQuantity
                        fuelGradeCode
                        itemUnitPriceAmount
                        fuelUomCode
                        fuelUomDescription
                        fuelUomDescriptionFr
                        fuelGradeDescription
                        fuelGradeDescriptionFr
                      }
                      tenderArray {
                        tenderTypeCode
                        tenderSubTypeCode
                        tenderDescription
                        amountTender
                        displayAccountNumber
                        sequenceNumber
                        approvalNumber
                        responseCode
                        tenderTypeName
                        transactionID
                        merchantID
                        entryMethod
                        tenderAcctTxnNumber
                        tenderAuthorizationCode
                        tenderTypeNameFr
                        tenderEntryMethodDescription
                        walletType
                        walletId
                        storedValueBucket
                      }
                      subTaxes {
                        tax1
                        tax2
                        tax3
                        tax4
                        aTaxPercent
                        aTaxLegend
                        aTaxAmount
                        bTaxPercent
                        bTaxLegend
                        bTaxAmount
                        cTaxPercent
                        cTaxLegend
                        cTaxAmount
                        dTaxAmount
                      }
                      instantSavings
                      membershipNumber
                    }
                  }
                }
            `.replace(/\s+/g, " "),
            variables: { startDate, endDate }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                const data = xhr.response?.data?.receiptsWithCounts?.receipts || [];
                resolve(data);
            } else {
                reject(`HTTP Error ${xhr.status}`);
            }
        };

        xhr.onerror = () => reject("Network error while contacting Costco API.");

        xhr.send(JSON.stringify(payload));
    });
}

// ======================================================================
// 2. Download JSON File
// ======================================================================

async function downloadReceipts() {
    const start = FROM_DATE;
    const end = TO_DATE;

    try {
        const receipts = await fetchReceipts(start, end);

        console.log(`📦 Retrieved ${receipts.length} receipts.`);
        console.log("Preparing JSON file...");

        const filename = `costco-raw-${start.replace(/\//g, "-")}-to-${end.replace(/\//g, "-")}.json`;

        const blob = new Blob([JSON.stringify(receipts, null, 2)], {
            type: "application/json"
        });

        const link = document.createElement("a");
        link.download = filename;
        link.href = URL.createObjectURL(blob);
        link.click();

        console.log("✅ Download complete!");

    } catch (err) {
        console.error("❌ Failed to download receipts:", err);
    }
}

// ======================================================================
// 3. Run Script
// ======================================================================

await downloadReceipts();
