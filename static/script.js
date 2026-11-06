const API_BASE = "http://127.0.0.1:5000";
const button_compare = document.getElementById("compare-button");
const button_update = document.getElementById("update-button");

async function loadIndustries(dropdownId) {
  const response = await fetch(`${API_BASE}/api/industries`);
  const data = await response.json();

  const select = document.getElementById(dropdownId);
  select.innerHTML = ""; // clear the "Loading..." placeholder

  data.industries.forEach(industry => {
    const option = document.createElement("option");
    option.value = industry;
    option.textContent = industry;
    select.appendChild(option);
  });
}

async function getIndustryData(industryNames) {
    const names = encodeURIComponent(industryNames.join(","));

    const response = await fetch(
        `${API_BASE}/api/industries/${names}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch industry data");
    }

    const data = await response.json();

    return data;
}

async function detailChange(industry, selected) {
    const response_demand = await fetch(
        `${API_BASE}/api/industries/${industry}`
    );

    if (!response_demand.ok) {
        throw new Error("Failed to fetch industry data");
    }

    const demanddata = await response_demand.json();
    const quarter1 = (demanddata[demanddata.length - 1][industry]);
    const quarter2 = (demanddata[demanddata.length - 5][industry]);
    const change = ((quarter1 - quarter2)/quarter2) * 100;

    let salary = 0

    if (industry === "Private households" || industry === "Total services" || industry === "All Jobs"){
        salary = 0
    } else{   
        const response_salary = await fetch(
        `${API_BASE}/api/industries/${industry}/salary`
        );

        if (!response_salary.ok) {
            throw new Error("Failed to fetch industry data");
        }
        const salarydata = await response_salary.json();
        salary = (salarydata[0]["Mean_Salary"]);
    }

    let demandElement = null;
    let salaryElement = null;

    if (selected === "left"){
        demandElement = document.getElementById("demand-change1");
        salaryElement = document.getElementById("mean-salary1");
    } else{
        demandElement = document.getElementById("demand-change2")
        salaryElement = document.getElementById("mean-salary2");
    }

    demandElement.textContent = change.toFixed(2) + "%";
    salaryElement.textContent = 
    salary.toLocaleString("en-GB", {
        style: "currency",
        currency: "GBP",
        maximumFractionDigits: 0
    });
}

function prepareChartData(data, industryNames) {
    const labels = data.map(row => row.Date);

    const datasets = industryNames.map(industry => ({
        label: industry,
        data: data.map(row => row[industry]),
        tension: 0.2
    }));

    return {
        labels: labels,
        datasets: datasets
    };
}

let industryChart = null;

function createChart(chartData) {
    const ctx = document.getElementById("trend-chart");

    if (industryChart) {
        industryChart.destroy();
    }

    industryChart = new Chart(ctx, {
        type: "line",
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: "index",
                intersect: false
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Date",
                        color: "teal", // Set the color of the x-axis title to teal
                        font: {
                            size: 22, // Set the font size of the x-axis title
                            family: 'inter', // Set the font family of the x-axis title
                        }
                    },
                    ticks: {
                        color: "white", // Set the color of the x-axis labels to white
                        size: 16 // Set the font size of the x-axis labels
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Amount of Jobs (thousands)",
                        color: "teal", // Set the color of the y-axis title to teal
                        font: {
                            size: 22, // Set the font size of the y-axis title
                            family: 'inter', // Set the font family of the y-axis title
                        }
                    },
                    beginAtZero: false,
                    ticks: {
                        color: "white", // Set the color of the y-axis labels to white
                        size: 16, // Set the font size of the y-axis labels
                    }
                }
            }
        }
    });
}

loadIndustries("industry-select-left"); // Load industries when the page loads

function updateChart() {
    const industry1 = document.getElementById("industry-select-left").value;
    const industry2 = document.getElementById("industry-select-right") ? document.getElementById("industry-select-right").value : null;
    const industryNames = [industry1, industry2].filter(Boolean); // Filter out null or empty values
    
    getIndustryData(industryNames)
        .then(data => {
            const chartData = prepareChartData(data, industryNames);
            createChart(chartData);
        })
        .catch(error => {
            console.error("Error fetching industry data:", error);
        });
    
        detailChange(industry1, "left")
    
    if (industry2 !== null) {
        detailChange(industry2, "right")
    }
}

function addIndustry() { //Adds another industry to compare when the button is clicked
  document.querySelector("#industry2").innerHTML = `
  <select id="industry-select-right">
    <option value="">Loading industries...</option>
  </select>

  <button id="remove-industry">Remove Industry</button>

  <div class = "description-container">

    <div class = "description">
      <h3>Mean Salary</h3>
      <p id ="mean-salary2">N/A</p>
    </div>

    <div class = "description">
      <h3>Change in Jobs</h3>
      <p id= "demand-change2">N/A</p>
    </div>
  </div>
  `; 

  loadIndustries("industry-select-right"); //Load industries for the second dropdown

  const button_remove = document.getElementById("remove-industry"); //Add event listener to the remove button to clear the second industry when clicked
  button_remove.addEventListener("click", function() {
    document.querySelector("#industry2").innerHTML = "";
    button_compare.disabled = false; //Enables the compare button again after removing the second industry
  });
}

button_compare.addEventListener("click", function() {
  button_compare.disabled = true; //Disable the button to prevent multiple clicks
  addIndustry();
});

button_update.addEventListener("click", function() {
  updateChart();
})