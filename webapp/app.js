const transactionsInput = document.getElementById("transactions-file");
const balancesInput = document.getElementById("balances-file");
const reconcileBtn = document.getElementById("reconcile-btn");
const errorBanner = document.getElementById("error-banner");
const results = document.getElementById("results");

let latestData = null;

function updateButtonState() {
  reconcileBtn.disabled = !(transactionsInput.files.length && balancesInput.files.length);
}
transactionsInput.addEventListener("change", updateButtonState);
balancesInput.addEventListener("change", updateButtonState);

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}
function clearError() {
  errorBanner.hidden = true;
  errorBanner.textContent = "";
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}

function formatMoney(value) {
  const sign = value < 0 ? "-" : "";
  return `${sign}$${Math.abs(value).toFixed(2)}`;
}

reconcileBtn.addEventListener("click", async () => {
  clearError();
  const transactionsFile = transactionsInput.files[0];
  const balancesFile = balancesInput.files[0];

  if (!transactionsFile.name.toLowerCase().endsWith(".csv") || !balancesFile.name.toLowerCase().endsWith(".csv")) {
    showError("Both files must be .csv files.");
    return;
  }

  reconcileBtn.disabled = true;
  reconcileBtn.textContent = "Reconciling…";

  try {
    const [transactionsText, balancesText] = await Promise.all([
      readFileAsText(transactionsFile),
      readFileAsText(balancesFile),
    ]);

    const response = await fetch("/api/reconcile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transactions_csv: transactionsText,
        balances_csv: balancesText,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      showError(data.error || "Something went wrong.");
      results.hidden = true;
      return;
    }

    latestData = data;
    renderResults(data);
  } catch (err) {
    showError(`Could not read or process files: ${err.message}`);
  } finally {
    reconcileBtn.disabled = false;
    reconcileBtn.textContent = "Reconcile";
    updateButtonState();
  }
});

function renderResults(data) {
  results.hidden = false;

  document.getElementById("expected-balance").textContent = formatMoney(data.expected_balance_latest);
  document.getElementById("expected-balance-date").textContent = `as of ${data.latest_date}`;
  document.getElementById("actual-balance").textContent = formatMoney(data.actual_balance_latest);
  document.getElementById("actual-balance-date").textContent = `as of ${data.latest_date}`;

  const totalCard = document.getElementById("total-discrepancy-card");
  const totalNote = document.getElementById("total-discrepancy-note");
  document.getElementById("total-discrepancy").textContent = formatMoney(data.total_discrepancy);
  document.getElementById("cumulative-discrepancy").textContent = formatMoney(data.total_discrepancy);

  totalCard.classList.remove("reconciled", "warning", "mismatched");
  if (!data.reconciled) {
    totalCard.classList.add("mismatched");
    totalNote.textContent = "Accounts do not reconcile.";
  } else if (data.warning) {
    totalCard.classList.add("warning");
    totalNote.textContent = "Accounts reconcile, but discrepancies were flagged along the way.";
  } else {
    totalCard.classList.add("reconciled");
    totalNote.textContent = "Accounts reconcile.";
  }

  renderTimeline(data);
  renderDatePicker(data);
  renderTable(data);
}

function renderTimeline(data) {
  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";

  const significantDates = Object.keys(data.significant_days).sort();
  if (significantDates.length === 0) {
    const empty = document.createElement("div");
    empty.className = "timeline-empty";
    empty.textContent = "No significant discrepancies found.";
    timeline.appendChild(empty);
    return;
  }

  for (const date of significantDates) {
    const delta = data.significant_days[date];
    const item = document.createElement("div");
    item.className = `timeline-item ${delta > 0 ? "increase" : "decrease"}`;

    const dateEl = document.createElement("span");
    dateEl.className = "timeline-date";
    dateEl.textContent = date;

    const summaryEl = document.createElement("span");
    summaryEl.textContent = data.summaries[date];

    item.appendChild(dateEl);
    item.appendChild(summaryEl);
    timeline.appendChild(item);
  }
}

function renderDatePicker(data) {
  const picker = document.getElementById("date-picker");
  const summaryEl = document.getElementById("date-summary");
  picker.min = data.dates[0];
  picker.max = data.dates[data.dates.length - 1];
  picker.value = "";
  summaryEl.textContent = "";

  picker.onchange = () => {
    const date = picker.value;
    if (!data.summaries.hasOwnProperty(date)) {
      summaryEl.textContent = `No data for ${date}.`;
      return;
    }
    const discrepancy = data.cumulative_discrepancy[date];
    summaryEl.textContent = `${data.summaries[date]} (discrepancy on this date: ${formatMoney(discrepancy)})`;
  };
}

function renderTable(data) {
  const tbody = document.querySelector("#detail-table tbody");
  tbody.innerHTML = "";

  for (const date of data.dates) {
    const row = document.createElement("tr");
    if (data.significant_days.hasOwnProperty(date)) {
      row.classList.add("significant");
    }

    const cells = [
      date,
      formatMoney(data.expected_balance[date]),
      formatMoney(data.actual_balance[date] ?? 0),
      formatMoney(data.cumulative_discrepancy[date]),
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      td.textContent = value;
      row.appendChild(td);
    }
    tbody.appendChild(row);
  }
}
