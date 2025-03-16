document.addEventListener('DOMContentLoaded', function() {
    fetch('/graphique_ppg_emg')
        .then(response => response.json())
        .then(data => {
            if (data.emg_values) {
                const emgValues = data.emg_values;
                console.log('Données EMG :', emgValues);

                // Extraire les valeurs et les heures EMG
                let valeursEmg = emgValues.map(item => item.valeur);
                let heuresEmg = emgValues.map(item => {
                    let heure = item.heure; // Format "YYYY-MM-DD HH:MM:SS"
                    let date = new Date(heure); // Convertir en objet Date pour les comparaisons
                    date.setHours(date.getHours() - 1); // Réduire l'heure d'une heure
                    return date; // Retourner la nouvelle heure ajustée
                });

                // Calculer la moyenne de la série
                const moyenneSerie = calculateMean(valeursEmg);
                console.log('Moyenne de la série :', moyenneSerie);

                // Déterminer le point le plus haut de la série
                const pointPlusHaut = Math.max(...valeursEmg);
                console.log('Point le plus haut de la série :', pointPlusHaut);

                // Diviser le point le plus haut par la moyenne
                const resultat = pointPlusHaut - moyenneSerie;
                console.log('Résultat (Point le plus haut - Moyenne) :', resultat);

                const final = resultat / 100;
                console.log('Indice à rentrer :', final);

                // Détection des points brutaux
                const pointsBrutaux = detectBrutalPoints(valeursEmg, 20, final); // Adapter en fonction de la plage de variations des valeurs emg
                console.log('Points Brutaux :', pointsBrutaux);

                // Division des valeurs EMG en segments
                const segments = divideByPoints(valeursEmg, pointsBrutaux, heuresEmg);
                console.log('Segments :', segments);

                // Trier les segments par ordre croissant d'heure de début
                segments.sort((a, b) => a.start - b.start);

                // Créer le graphique avec les données EMG
                createEMGChart(valeursEmg, heuresEmg.map(date => date.toTimeString().substring(0, 8)), pointsBrutaux, segments);
            } else {
                console.error('Aucune donnée EMG trouvée.');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données EMG :', error);
        });
});

// Fonction pour calculer la moyenne
function calculateMean(values) {
    const sum = values.reduce((acc, val) => acc + val, 0);
    return sum / values.length;
}

// Fonction pour calculer la pente
function calculateSlope(values) {
    const x = Array.from({ length: values.length }, (_, i) => i);
    const y = values;
    if (x.length > 1) {
        return (y[y.length - 1] - y[0]) / (x[x.length - 1] - x[0]);
    } else {
        return 0;
    }
}

// Fonction pour calculer la courbe de tendance (régression linéaire)
function calculateTrendLine(values) {
    const n = values.length;
    const sumX = (n - 1) * n / 2; // Somme des indices
    const sumY = values.reduce((acc, val) => acc + val, 0);
    const sumXY = values.reduce((acc, val, i) => acc + i * val, 0);
    const sumX2 = (n - 1) * n * (2 * n - 1) / 6; // Somme des carrés des indices

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    return { slope, intercept };
}

// Fonction pour détecter les points brutaux
function detectBrutalPoints(emgValues, groupSize = 20, seuilDiff = 0.5) {
    const points = [];
    const moyenneMobile = emgValues.map((_, i) => {
        const start = Math.max(0, i - groupSize + 1);
        const end = i + 1;
        const window = emgValues.slice(start, end);
        return window.reduce((acc, val) => acc + val, 0) / window.length;
    }).slice(groupSize - 1);

    let i = 0;
    while (i < moyenneMobile.length - 30) {
        const valeursPremierePeriode = moyenneMobile.slice(i, i + 20);
        const pentePremiere = calculateSlope(valeursPremierePeriode);
        const valeursSecondePeriode = moyenneMobile.slice(i + 20, i + 40);
        const penteSeconde = calculateSlope(valeursSecondePeriode);

        if (Math.abs(pentePremiere - penteSeconde) < seuilDiff) {
            i += 20;
        } else {
            points.push(i + 20);
            i += 20;
        }
    }
    return points;
}

// Fonction pour diviser les valeurs EMG en segments
function divideByPoints(emgValues, pointsBrutaux, heuresEmg) {
    const segments = [];
    let startIdx = 0;
    pointsBrutaux.forEach(point => {
        const endIdx = point;
        const segment = emgValues.slice(startIdx, endIdx);
        const startTime = heuresEmg[startIdx];
        const endTime = heuresEmg[endIdx];
        const duration = (endTime - startTime) / 1000 / 60; // Durée en minutes

        if (duration > 1) {
            segments.push({ start: startIdx, end: endIdx, segment });
        }
        startIdx = endIdx;
    });

    // Vérifier le dernier segment
    const lastSegment = emgValues.slice(startIdx);
    const lastStartTime = heuresEmg[startIdx];
    const lastEndTime = heuresEmg[heuresEmg.length - 1];
    const lastDuration = (lastEndTime - lastStartTime) / 1000 / 60; // Durée en minutes

    if (lastDuration > 1) {
        segments.push({ start: startIdx, end: emgValues.length, segment: lastSegment });
    }

    return segments;
}

// Fonction pour créer le graphique avec les données EMG
function createEMGChart(emgValues, heuresEmg, pointsBrutaux, segments) {
    const ctx = document.getElementById('myChartEMG').getContext('2d');

    const datasets = [{
        label: 'Valeurs EMG',
        data: emgValues,
        borderColor: 'rgb(105, 208, 208, 0.9)',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
    }];

    let greenCount = 0;
    let redCount = 0;
    const greenDetails = [];
    const redDetails = [];
    const annotations = [];

    segments.forEach(segment => {
        // Ajuster les valeurs du segment pour accentuer les variations
        const penteGlobale = calculateSlope(segment.segment);
        const adjustedSegment = segment.segment.map((val, i) => val + penteGlobale * i);

        // Calculer la courbe de tendance
        const { slope, intercept } = calculateTrendLine(adjustedSegment);
        console.log(`Courbe de tendance pour le segment ${segment.start}-${segment.end}: y = ${slope.toFixed(2)}x + ${intercept.toFixed(2)}`);

        // Attribuer la couleur en fonction du coefficient directeur
        const color = slope >= 0 ? 'rgb(47, 217, 143)' : 'rgb(255, 138, 138)';

        const xVals = Array.from({ length: segment.segment.length }, (_, i) => segment.start + i);
        const yVals = adjustedSegment;

        const labelText = `Pente moyenne : ${slope.toFixed(2)}`;

        // Ajouter les informations aux tableaux de détails
        const heureDebut = heuresEmg[segment.start];
        const heureFin = heuresEmg[segment.end];

        if (color === 'rgb(47, 217, 143)') {
            greenDetails.push(`${heureDebut} - ${heureFin}`);
            greenCount++;
        } else {
            redDetails.push(`${heureDebut} - ${heureFin}`);
            redCount++;
        }

        datasets.push({
            label: `Segment ${heureDebut} à ${heureFin}`,
            data: yVals.map((y, i) => ({ x: xVals[i], y })),
            borderColor: color,
            borderWidth: 1,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
        });

        // Ajouter une annotation pour colorier l'intervalle
        annotations.push({
            type: 'box',
            xMin: segment.start,
            xMax: segment.end,
            backgroundColor: color === 'rgb(47, 217, 143)' ? 'rgba(181, 253, 181, 0)' : 'rgba(252, 201, 201, 0)',
            borderWidth: 0
        });

        // Ajouter des lignes verticales jaunes pour marquer le début et la fin des segments
        annotations.push({
            type: 'line',
            scaleID: 'x',
            value: segment.start,
            borderColor: 'rgba(253, 160, 0, 0)',
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
                enabled: false,
                content: 'Début',
                position: 'start'
            }
        });

        annotations.push({
            type: 'line',
            scaleID: 'x',
            value: segment.end,
            borderColor: 'rgba(253, 160, 0, 0.01)',
            borderWidth: 1,
            borderDash: [5, 5],
            label: {
                enabled: false,
                content: 'Fin',
                position: 'end'
            }
        });
    });

    // Mettre à jour le graphique
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: emgValues.length }, (_, i) => i),
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Temps'
                    },
                    ticks: {
                        callback: function(value, index, values) {
                            return index % 1 === 0 ? heuresEmg[value] : '';
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Valeur EMG'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        boxWidth: 10,
                        font: {
                            size: 10
                        }
                    }
                },
                tooltip: {
                    enabled: true
                },
                annotation: {
                    annotations: annotations
                }
            }
        }
    });

    // Mettre à jour les informations dans le HTML
    const greenContainer = document.querySelector('.bottom-green-container');
    const redContainer = document.querySelector('.bottom-red-container');
    const blankContainer = document.querySelector('.blank-container');

    if (greenCount > 0) {
        greenContainer.classList.add('show');
        greenContainer.innerHTML = `Nombre d'augmentation: ${greenCount}<br><br>Détails : <br>${greenDetails.join('<br>')}`;
    } else {
        greenContainer.classList.remove('show');
    }

    if (redCount > 0) {
        redContainer.classList.add('show');
        redContainer.innerHTML = `Nombre de diminution: ${redCount}<br><br>Détails : <br>${redDetails.join('<br>')}`;
    } else {
        redContainer.classList.remove('show');
    }

    if (greenCount > 0 || redCount > 0) {
        blankContainer.classList.add('show');
        blankContainer.innerHTML = `Nombre total de changement de rythme : ${greenCount + redCount}`;
    } else {
        blankContainer.classList.remove('show');
    }
}
