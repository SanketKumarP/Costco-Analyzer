// content.js
// Listens for events from the popup and runs the Costco GraphQL query
// directly in the Costco tab context.

document.addEventListener("COSTCO_DOWNLOAD_RECEIPTS", async (e) => {
    const { start, end } = e.detail;

    console.log("📡 Costco Receipt Downloader: requested range", start, "→", end);

    async function fetchReceipts(startDate, endDate) {
        console.log("📡 Fetching receipts from Costco API…");

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.responseType = "json";

            xhr.open(
                "POST",
                "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"
            );

            // Required Costco headers – pulled from page localStorage
            xhr.setRequestHeader("Content-Type", "application/json-patch+json");
            xhr.setRequestHeader("Costco.Env", "ecom");
            xhr.setRequestHeader("Costco.Service", "restOrders");
            xhr.setRequestHeader(
                "Costco-X-Wcs-Clientid",
                localStorage.getItem("clientID")
            );
            xhr.setRequestHeader(
                "Client-Identifier",
                "481b1aec-aa3b-454b-b81b-48187e28f205"
            );
            xhr.setRequestHeader(
                "Costco-X-Authorization",
                "Bearer " + localStorage.getItem("idToken")
            );

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
                    const receipts =
                        xhr.response?.data?.receiptsWithCounts?.receipts || [];
                    resolve(receipts);
                } else {
                    reject(`HTTP error ${xhr.status}`);
                }
            };

            xhr.onerror = () => {
                reject("Network error while contacting Costco API.");
            };

            xhr.send(JSON.stringify(payload));
        });
    }

    async function downloadReceipts() {
        try {
            console.log("📥 Starting download for range:", start, "→", end);

            const receipts = await fetchReceipts(start, end);
            console.log(`✅ Costco API returned ${receipts.length} receipts.`);

            if (!Array.isArray(receipts) || receipts.length === 0) {
                alert(
                    `No receipts found between ${start} and ${end}.\n` +
                    `Make sure you have purchases in this range and you're logged in.`
                );
                return;
            }

            const filename = `costco-raw-${start.replace(/\//g, "-")}-to-${end.replace(
                /\//g,
                "-"
            )}.json`;

            const blob = new Blob([JSON.stringify(receipts, null, 2)], {
                type: "application/json"
            });

            const a = document.createElement("a");
            a.download = filename;
            a.href = window.URL.createObjectURL(blob);
            a.click();

            alert(
                `Downloaded ${receipts.length} receipts.\n\n` +
                `File: ${filename}\n\n` +
                `You can now upload this JSON into your Streamlit dashboard.`
            );
        } catch (err) {
            console.error("❌ Failed to download receipts:", err);
            alert(
                "Error downloading Costco receipts:\n\n" +
                String(err)
            );
        }
    }

    downloadReceipts();
});
