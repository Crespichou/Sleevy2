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
        label: "Tendance du rythme cardiaque au repos",
        data: trendLineData,
        borderColor: 'rgba(2, 48, 2, 0.69)',
        borderWidth: 2,
        fill: false,
        pointRadius: 0,
        tension: 0.4
    });

    // Calculer l'aire entre la courbe de session actuelle et la courbe de tendance du rythme cardiaque au repos
    const areaCurrentSession = calculateAreaBetweenCurves(cumulativeVariabilities[highestSessionLabel], trendLineData);

    // Calculer l'aire sous la courbe de tendance
    const areaTrendLine = calculateAreaUnderCurve(trendLineData);

    console.log("Aire entre la courbe de la session actuelle et la courbe de tendance :", areaCurrentSession);
    console.log("Aire sous la courbe de tendance :", areaTrendLine);

    let percentageOtherSessions = 0;
    let areaOtherSessions = 0;
    let percentageTrendLine = 0;

    // Vérifier s'il y a plus d'une session
    if (groupLabels.length > 1) {
        const meanOfOtherSessions = calculateMeanOfOtherSessions(cumulativeVariabilities, highestSessionLabel);
        areaOtherSessions = calculateAreaBetweenCurves(meanOfOtherSessions, trendLineData);

        // Calculer le pourcentage de la première aire par rapport à la seconde
        percentageOtherSessions = (areaCurrentSession / areaOtherSessions) * 100;

        console.log("Aire entre la moyenne des autres sessions et la courbe de tendance :", areaOtherSessions);
        console.log("Pourcentage de la première aire par rapport à la seconde :", percentageOtherSessions.toFixed(2) + "%");

        // Mettre à jour le HTML pour afficher les résultats
        //document.getElementById('correlation-percentage').innerHTML = `
            //Aire entre la courbe de la session actuelle et la courbe de tendance : ${areaCurrentSession.toFixed(2)}<br>
            //Aire entre la moyenne des autres sessions et la courbe de tendance : ${areaOtherSessions.toFixed(2)}<br>
            //Aire sous la courbe de tendance : ${areaTrendLine.toFixed(2)}<br>
            //Pourcentage de la première aire par rapport à la seconde : ${percentageOtherSessions.toFixed(2)}%
        //`;

        // Mettre à jour la variable CSS pour le pourcentage
        const progressBar = document.querySelector('[role="progressbar"]');
        progressBar.style.setProperty('--value', percentageOtherSessions.toFixed(2));
        progressBar.setAttribute('data-label', `${percentageOtherSessions.toFixed(2)}%`);
    } else {
        // Calculer le pourcentage de l'aire entre la courbe de la session actuelle et la courbe de tendance par rapport à l'aire sous la courbe de tendance
        percentageTrendLine = (areaCurrentSession / areaTrendLine) * 100;

        console.log("Aucune autre session disponible pour calculer l'aire.");
        //document.getElementById('correlation-percentage').innerHTML = `
            //Aire entre la courbe de la session actuelle et la courbe de tendance : ${areaCurrentSession.toFixed(2)}<br>
            //Aire sous la courbe de tendance : ${areaTrendLine.toFixed(2)}<br>
            //Pourcentage de la première aire par rapport à l'aire sous la courbe de tendance : ${percentageTrendLine.toFixed(2)}%<br>
            //Aucune autre session disponible pour calculer l'aire.
        //`;

        // Mettre à jour la variable CSS pour le pourcentage
        const progressBar = document.querySelector('[role="progressbar"]');
        progressBar.style.setProperty('--value', percentageTrendLine.toFixed(2));
        progressBar.setAttribute('data-label', `${percentageTrendLine.toFixed(2)}%`);
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

function calculateAreaBetweenCurves(curve1, curve2) {
    let area = 0;
    const minLength = Math.min(curve1.length, curve2.length);
    for (let i = 0; i < minLength; i++) {
        area += Math.abs(curve1[i] - curve2[i]);
    }
    return area;
}

function calculateAreaUnderCurve(curve) {
    let area = 0;
    for (let i = 0; i < curve.length; i++) {
        area += curve[i];
    }
    return area;
}

function calculateMeanOfOtherSessions(cumulativeVariabilities, highestSessionLabel) {
    const otherSessions = Object.keys(cumulativeVariabilities).filter(label => label !== highestSessionLabel);
    const sum = otherSessions.reduce((acc, label) => {
        return acc.concat(cumulativeVariabilities[label]);
    }, []);
    const count = sum.length;
    const mean = Array.from({ length: count }, () => 0);

    otherSessions.forEach(label => {
        for (let i = 0; i < cumulativeVariabilities[label].length; i++) {
            mean[i] += cumulativeVariabilities[label][i] / otherSessions.length;
        }
    });

    return mean;
}
