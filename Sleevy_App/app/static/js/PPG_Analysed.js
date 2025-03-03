document.addEventListener("DOMContentLoaded", function () {
    fetch('/graphique_ppg_toutes_sessions')
        .then(response => response.json())
        .then(data => {
            console.log("Données PPG reçues :", data);
            processAndDisplayData(data);
        })
        .catch(error => console.error("Erreur lors de la récupération des données :", error));
});

function processAndDisplayData(data) {
    console.log("Données reçues pour le traitement :", data);

    const referenceValues = data.referenceValues;
    const referenceMean = calculateMean(referenceValues);
    console.log("Moyenne des valeurs de référence :", referenceMean);

    const datasets = {};
    Object.keys(data.ppg_sessions).forEach(sessionId => {
        datasets[`Session_${sessionId}`] = data.ppg_sessions[sessionId];
    });

    const cumulativeVariabilities = {};
    Object.keys(datasets).forEach(label => {
        cumulativeVariabilities[label] = computeCumulativeVariability(datasets[label], referenceMean);
    });

    const variabilities = calculateVariabilities(datasets, referenceMean);
    const tolerance = 0.2 * Object.values(variabilities).reduce((a, b) => a + b, 0) / Object.values(variabilities).length;
    const groups = groupDatasetsByVariability(variabilities, tolerance);

    console.log("Groupes formés :", groups);

    const highestSessionId = Math.max(...Object.keys(data.ppg_sessions).map(Number));
    const highestSessionLabel = `Session_${highestSessionId}`;
    let groupToDisplay = null;

    Object.keys(groups).forEach(groupVariability => {
        if (groups[groupVariability].includes(highestSessionLabel)) {
            groupToDisplay = groups[groupVariability];
        }
    });

    if (groupToDisplay) {
        console.log("Groupe à afficher :", groupToDisplay);
        displayGroupedData(groupToDisplay, datasets, referenceMean, highestSessionLabel);
        displaySecondaryData(groupToDisplay, cumulativeVariabilities, highestSessionLabel, referenceValues, referenceMean);
    } else {
        console.error("Aucun groupe trouvé pour la session avec le session_id le plus élevé.");
    }
}

function calculateMean(values) {
    const sum = values.reduce((acc, val) => acc + val, 0);
    return sum / values.length;
}

function computeCumulativeVariability(data, fixedMean) {
    let cumulativeVariability = [];
    let currentVariability = 0;
    data.forEach(value => {
        if (value !== null) {
            currentVariability += Math.abs(value - fixedMean);
            cumulativeVariability.push(currentVariability);
        }
    });
    return cumulativeVariability;
}

function calculateVariabilities(datasets, referenceMean) {
    const variabilities = {};
    Object.keys(datasets).forEach(label => {
        variabilities[label] = datasets[label].reduce((sum, value) => {
            if (value !== null) {
                return sum + Math.abs(value - referenceMean);
            }
            return sum;
        }, 0);
    });
    return variabilities;
}

function groupDatasetsByVariability(variabilities, tolerance) {
    const groups = {};
    Object.keys(variabilities).forEach(label => {
        const variability = variabilities[label];
        let addedToGroup = false;
        Object.keys(groups).forEach(groupVariability => {
            if (Math.abs(variability - parseFloat(groupVariability)) <= tolerance) {
                groups[groupVariability].push(label);
                addedToGroup = true;
            }
        });
        if (!addedToGroup) {
            groups[variability] = [label];
        }
    });
    return groups;
}

function displayGroupedData(groupLabels, datasets, referenceMean, highestSessionLabel) {
    const ctx = document.getElementById('myChartPPG').getContext('2d');

    if (window.myChartPPG && typeof window.myChartPPG.destroy === 'function') {
        window.myChartPPG.destroy();
    }

    const groupedDatasets = [];

    groupLabels.forEach(label => {
        groupedDatasets.push({
            label: label === highestSessionLabel ? "Session actuelle" : "Autres sessions",
            data: datasets[label],
            borderColor: label === highestSessionLabel ? 'blue' : 'gray',
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
            tension: 0.4
        });
    });

    window.myChartPPG = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: Math.max(...Object.values(datasets).map(arr => arr.length)) }, (_, i) => i + 1),
            datasets: groupedDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Itérations'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Valeur PPG'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });

    console.log("Graphique du groupe affiché :", window.myChartPPG);
}

function calculateTrendLine(x, y) {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xVal, index) => sum + xVal * y[index], 0);
    const sumX2 = x.reduce((sum, xVal) => sum + xVal * xVal, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    return { slope, intercept };
}

function displaySecondaryData(groupLabels, cumulativeVariabilities, highestSessionLabel, referenceValues, referenceMean) {
    const ctx2 = document.getElementById('myChartPPG2').getContext('2d');

    if (window.myChartPPG2 && typeof window.myChartPPG2.destroy === 'function') {
        window.myChartPPG2.destroy();
    }

    const secondaryDatasets = [];

    groupLabels.forEach(label => {
        secondaryDatasets.push({
            label: label === highestSessionLabel ? "Session actuelle" : "Autres sessions",
            data: cumulativeVariabilities[label],
            borderColor: label === highestSessionLabel ? 'blue' : 'gray',
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
            tension: 0.4
        });
    });

    // Ajouter la variabilité des referenceValues
    const referenceVariability = computeCumulativeVariability(referenceValues, referenceMean);
    secondaryDatasets.push({
        label: "Rythme cardiaque au repos",
        data: referenceVariability,
        borderColor: 'rgba(2, 48, 2, 0.69)',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
        tension: 0.4
    });

    // Calculer la ligne de tendance pour referenceVariability
    const xValues = Array.from({ length: referenceVariability.length }, (_, i) => i + 1);
    const { slope, intercept } = calculateTrendLine(xValues, referenceVariability);

    // Étendre la ligne de tendance pour couvrir la même plage que les autres courbes
    const maxLength = Math.max(...Object.values(cumulativeVariabilities).map(arr => arr.length));
    const trendLineData = Array.from({ length: maxLength }, (_, i) => slope * (i + 1) + intercept);

    secondaryDatasets.push({
        label: "Rythme cardiaque au repos",
        data: trendLineData,
        borderColor: 'rgba(2, 48, 2, 0.69)',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
        tension: 0.4
    });

    window.myChartPPG2 = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: Array.from({ length: maxLength }, (_, i) => i + 1),
            datasets: secondaryDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Itérations'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Variabilité cumulée'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });

    console.log("Graphique secondaire affiché :", window.myChartPPG2);
}
