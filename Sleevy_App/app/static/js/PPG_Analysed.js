document.addEventListener("DOMContentLoaded", function () {
    fetch('/graphique_ppg_toutes_sessions')  // Récupère toutes les sessions PPG
        .then(response => response.json())
        .then(data => {
            console.log("Données PPG reçues :", data);
            processAndDisplayData(data);
        })
        .catch(error => console.error("Erreur lors de la récupération des données :", error));
});

function processAndDisplayData(data) {
    console.log("Données reçues pour le traitement :", data);

    const referenceMean = 69.4; // Valeur de la référence moyenne
    const datasets = {};

    // Convertir les données reçues en un format utilisable
    Object.keys(data).forEach(sessionId => {
        datasets[`Session_${sessionId}`] = data[sessionId];
    });

    const cumulativeVariabilities = {};
    Object.keys(datasets).forEach(label => {
        cumulativeVariabilities[label] = computeCumulativeVariability(datasets[label], referenceMean);
    });

    const variabilities = calculateVariabilities(datasets, referenceMean);
    const tolerance = 0.2 * Object.values(variabilities).reduce((a, b) => a + b, 0) / Object.values(variabilities).length;
    const groups = groupDatasetsByVariability(variabilities, tolerance);

    console.log("Groupes formés :", groups);

    // Identifier le groupe contenant la session avec le session_id le plus élevé
    const highestSessionId = Math.max(...Object.keys(data).map(Number));
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
        displaySecondaryData(groupToDisplay, cumulativeVariabilities, highestSessionLabel);
    } else {
        console.error("Aucun groupe trouvé pour la session avec le session_id le plus élevé.");
    }
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
            borderColor: label === highestSessionLabel ? 'red' : 'black', // Mettre en rouge la courbe avec le session_id le plus élevé
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

function displaySecondaryData(groupLabels, cumulativeVariabilities, highestSessionLabel) {
    const ctx2 = document.getElementById('myChartPPG2').getContext('2d');

    if (window.myChartPPG2 && typeof window.myChartPPG2.destroy === 'function') {
        window.myChartPPG2.destroy();
    }

    const secondaryDatasets = [];

    groupLabels.forEach(label => {
        secondaryDatasets.push({
            label: label === highestSessionLabel ? "Session actuelle" : "Autres sessions",
            data: cumulativeVariabilities[label],
            borderColor: label === highestSessionLabel ? 'red' : 'black', // Mettre en rouge la courbe avec le session_id le plus élevé
            borderWidth: 2,
            fill: false,
            pointRadius: 0,
            tension: 0.4
        });
    });

    window.myChartPPG2 = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: Array.from({ length: Math.max(...Object.values(cumulativeVariabilities).map(arr => arr.length)) }, (_, i) => i + 1),
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
