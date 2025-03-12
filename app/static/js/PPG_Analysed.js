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

    // Ajouter la courbe de la session actuelle avec un dégradé
    const currentSessionData = datasets[highestSessionLabel];
    const gradientBlue = ctx.createLinearGradient(0, 0, 0, 400);
    gradientBlue.addColorStop(0, 'rgb(105, 208, 208,1)'); // Bleu semi-transparent
    gradientBlue.addColorStop(0.7, 'rgba(105, 208, 208, 0.19)'); // Transparent

    groupedDatasets.push({
        label: "Session actuelle",
        data: currentSessionData,
        borderColor:'rgb(105, 208, 208)',
        borderWidth: 2,
        fill: true,
        backgroundColor: gradientBlue,
        pointRadius: 0,
        tension: 0.4
    });

    // Vérifier si des courbes d'autres sessions existent
    const otherSessionsLabels = groupLabels.filter(label => label !== highestSessionLabel);
    if (otherSessionsLabels.length > 0) {
        // Créer une courbe synthétique pour les autres sessions avec un dégradé
        const syntheticCurve = calculateSyntheticCurve(datasets, otherSessionsLabels);

        const gradientGray = ctx.createLinearGradient(0, 0, 0, 400);
        gradientGray.addColorStop(0, 'rgba(173, 0, 247, 0.4)'); // Gris semi-transparent
        gradientGray.addColorStop(0.7, 'rgba(173, 0, 247, 0)'); // Transparent

        groupedDatasets.push({
            label: "Synthèse des autres sessions",
            data: syntheticCurve,
            borderColor: 'rgba(173, 0, 247, 0.4)',
            borderWidth: 2,
            fill: true,
            backgroundColor: gradientGray,
            pointRadius: 0,
            tension: 0.4
        });
    }

    // Déterminer la longueur maximale entre la session actuelle et la synthèse des autres sessions
    const maxLength = Math.max(currentSessionData.length, ...otherSessionsLabels.map(label => datasets[label].length));

    window.myChartPPG = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: maxLength }, (_, i) => i + 1),
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
                    },
                    grid:{
                        display : false
                    },
                    min: 0,
                    max: maxLength
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

function calculateSyntheticCurve(datasets, otherSessionsLabels) {
    const maxLength = Math.max(...otherSessionsLabels.map(label => datasets[label].length));
    const syntheticCurve = Array(maxLength).fill(0);

    for (let i = 0; i < maxLength; i++) {
        const valuesAtIndex = otherSessionsLabels
            .map(label => datasets[label][i] || 0)
            .filter(value => value !== 0);

        if (valuesAtIndex.length > 0) {
            syntheticCurve[i] = Math.max(...valuesAtIndex); // ou valuesAtIndex.reduce((a, b) => a + b, 0) / valuesAtIndex.length pour la moyenne
        }
    }

    return syntheticCurve;
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
            borderColor: label === highestSessionLabel ? 'rgb(105, 208, 208)' : 'rgba(173, 0, 247, 0.4)',
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
    const { slope: slopeTrendLine, intercept } = calculateTrendLine(xValues, referenceVariability);

    // Étendre la ligne de tendance pour couvrir la même plage que les autres courbes
    const maxLength = Math.max(...Object.values(cumulativeVariabilities).map(arr => arr.length));
    const trendLineData = Array.from({ length: maxLength }, (_, i) => slopeTrendLine * (i + 1) + intercept);

    secondaryDatasets.push({
        label: "Tendance du rythme cardiaque au repos",
        data: trendLineData,
        borderColor: 'rgba(2, 48, 2, 0.69)',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
        tension: 0.4
    });

    // Calculer la ligne de tendance pour la session actuelle
    const currentSessionData = cumulativeVariabilities[highestSessionLabel];
    const currentSessionXValues = Array.from({ length: currentSessionData.length }, (_, i) => i + 1);
    const currentSessionTrendLine = calculateTrendLine(currentSessionXValues, currentSessionData);
    const currentSessionTrendData = Array.from({ length: maxLength }, (_, i) => currentSessionTrendLine.slope * (i + 1) + currentSessionTrendLine.intercept);

    //secondaryDatasets.push({
        //label: "Tendance de la session actuelle",
        //data: currentSessionTrendData,
        //borderColor: 'blue',
        //borderWidth: 2,
        //fill: false,
        //pointRadius: 0,
        //tension: 0.4
    //});

    // Vérifier si des courbes d'autres sessions existent
    const otherSessionsLabels = groupLabels.filter(label => label !== highestSessionLabel);
    if (otherSessionsLabels.length > 0) {
        // Calculer la moyenne des courbes "autres sessions"
        const averageCurve = calculateAverageCurve(cumulativeVariabilities, otherSessionsLabels);

        //secondaryDatasets.push({
            //label: "Moyenne des autres sessions",
            //data: averageCurve,
            //borderColor: 'purple',
            //borderWidth: 2,
            //fill: false,
            //pointRadius: 0,
            //tension: 0.4
        //});

        // Calculer la ligne de tendance pour la moyenne des autres sessions
        const averageCurveXValues = Array.from({ length: averageCurve.length }, (_, i) => i + 1);
        const averageCurveTrendLine = calculateTrendLine(averageCurveXValues, averageCurve);
        const averageCurveTrendData = Array.from({ length: maxLength }, (_, i) => averageCurveTrendLine.slope * (i + 1) + averageCurveTrendLine.intercept);

        //secondaryDatasets.push({
            //label: "Tendance de la moyenne des autres sessions",
            //data: averageCurveTrendData,
            //borderColor: 'purple',
            //borderWidth: 2,
            //borderDash: [5, 5], // Ligne en pointillés pour la tendance
            //fill: false,
            //pointRadius: 0,
            //tension: 0.4
        //});

        // Calculer le pourcentage basé sur les coefficients directeurs
        const currentSlope = currentSessionTrendLine.slope;
        const averageSlope = averageCurveTrendLine.slope;
        const referenceSlope = slopeTrendLine;

        let correlationPercentage;
        if (currentSlope === averageSlope) {
            correlationPercentage = 50;
        } else if (currentSlope >= referenceSlope && currentSlope <= averageSlope) {
            const slopeRange = averageSlope - referenceSlope;
            const relativePosition = (currentSlope * 100) / slopeRange
            //const relativePosition = (currentSlope - referenceSlope) / slopeRange;
            correlationPercentage = 50 * (relativePosition/100);
        } else if (currentSlope > averageSlope) {
            const difference = currentSlope - averageSlope;
            const relativePosition = (difference / (averageSlope - referenceSlope)) * 100;
            const additionalPercentage = 50 * (relativePosition / 100);
            correlationPercentage = 50 + additionalPercentage;
        } else {
            // Si le coefficient directeur est en dehors de l'intervalle, fixer le pourcentage à 0% ou 100%
            correlationPercentage = currentSlope < referenceSlope ? 0 : 100;
        }


        console.log("Nouveau pourcentage de corrélation :", correlationPercentage.toFixed(2) + "%");

        // Mettre à jour la variable CSS pour le pourcentage
        const progressBar = document.querySelector('[role="progressbar"]');
        progressBar.style.setProperty('--value', correlationPercentage.toFixed(2));
        progressBar.setAttribute('data-label', `${correlationPercentage.toFixed(2)}%`);
    } else {
        // Si aucune courbe d'autres sessions n'existe, calculer le pourcentage avec les deux coefficients restants
        const currentSlope = currentSessionTrendLine.slope;
        const referenceSlope = slopeTrendLine;

        let correlationPercentage = (Math.max(currentSlope, referenceSlope) / Math.min(currentSlope, referenceSlope));

        // Décaler la virgule vers la gauche en divisant par 10
        correlationPercentage = correlationPercentage / 10;

        // Convertir en pourcentage
        correlationPercentage = correlationPercentage * 100;

        // Arrondir au centième le plus proche
        correlationPercentage = Math.round(correlationPercentage * 100) / 100;

        console.log("Pourcentage de corrélation basé sur les coefficients directeurs restants :", correlationPercentage + "%");

        // Mettre à jour la variable CSS pour le pourcentage
        const progressBar = document.querySelector('[role="progressbar"]');
        progressBar.style.setProperty('--value', correlationPercentage);
        progressBar.setAttribute('data-label', `${correlationPercentage}%`);
    }

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
                    },
                    grid:{
                        display : false
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
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            const datasetLabel = tooltipItem.dataset.label || '';
                            const value = tooltipItem.raw || 0;
                            let slopeLabel = '';

                            if (datasetLabel === "Session actuelle") {
                                slopeLabel = `Coefficient directeur : ${currentSessionTrendLine.slope.toFixed(2)}`;
                            } else if (datasetLabel === "Synthèse des autres sessions") {
                                slopeLabel = `Coefficient directeur : ${slopeTrendLine.toFixed(2)}`;
                            } else if (datasetLabel === "Tendance du rythme cardiaque au repos") {
                                slopeLabel = `Coefficient directeur : ${slopeTrendLine.toFixed(2)}`;
                            } else if (datasetLabel === "Tendance de la session actuelle") {
                                slopeLabel = `Coefficient directeur : ${currentSessionTrendLine.slope.toFixed(2)}`;
                            } else if (datasetLabel === "Tendance de la moyenne des autres sessions") {
                                slopeLabel = `Coefficient directeur : ${averageCurveTrendLine.slope.toFixed(2)}`;
                            }

                            return `${datasetLabel}: ${value} ${slopeLabel}`;
                        }
                    }
                }
            }
        }
    });

    console.log("Graphique secondaire affiché :", window.myChartPPG2);
}

function calculateAverageCurve(cumulativeVariabilities, otherSessionsLabels) {
    const maxLength = Math.max(...otherSessionsLabels.map(label => cumulativeVariabilities[label].length));
    const averageCurve = Array(maxLength).fill(0);

    for (let i = 0; i < maxLength; i++) {
        const valuesAtIndex = otherSessionsLabels
            .map(label => cumulativeVariabilities[label][i] || 0)
            .filter(value => value !== 0);

        if (valuesAtIndex.length > 0) {
            averageCurve[i] = valuesAtIndex.reduce((a, b) => a + b, 0) / valuesAtIndex.length;
        }
    }

    return averageCurve;
}

function calculateSlope(x, y) {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xVal, index) => sum + xVal * y[index], 0);
    const sumX2 = x.reduce((sum, xVal) => sum + xVal * xVal, 0);

    return (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
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

function calculateCorrelation(x, y) {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xVal, index) => sum + xVal * y[index], 0);
    const sumX2 = x.reduce((sum, xVal) => sum + xVal * xVal, 0);
    const sumY2 = y.reduce((sum, yVal) => sum + yVal * yVal, 0);

    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

    return numerator / denominator;
}
