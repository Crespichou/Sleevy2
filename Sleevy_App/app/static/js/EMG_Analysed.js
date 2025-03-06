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
                    return new Date(heure); // Convertir en objet Date pour les comparaisons
                });

                // Détection des points brutaux
                const pointsBrutaux = detectBrutalPoints(valeursEmg, 70, 0.45);
                console.log('Points Brutaux :', pointsBrutaux);

                // Division des valeurs EMG en segments
                const segments = divideByPoints(valeursEmg, pointsBrutaux);
                console.log('Segments :', segments);

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

// Fonction pour détecter les points brutaux
function detectBrutalPoints(emgValues, groupSize = 50, seuilDiff = 0.5) {
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
function divideByPoints(emgValues, pointsBrutaux) {
    const segments = [];
    let startIdx = 0;
    pointsBrutaux.forEach(point => {
        segments.push({ start: startIdx, end: point, segment: emgValues.slice(startIdx, point) });
        startIdx = point;
    });
    segments.push({ start: startIdx, end: emgValues.length, segment: emgValues.slice(startIdx) });
    return segments;
}

// Fonction pour créer le graphique avec les données EMG
function createEMGChart(emgValues, heuresEmg, pointsBrutaux, segments) {
    const ctx = document.getElementById('myChartEMG').getContext('2d');

    const datasets = [{
        label: 'Valeurs EMG',
        data: emgValues,
        borderColor: 'rgb(21, 0, 253)',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
    }];

    let greenCount = 0;
    let redCount = 0;
    const greenDetails = [];  // Tableau pour les détails des segments verts
    const redDetails = [];    // Tableau pour les détails des segments rouges

    segments.sort((a, b) => b.segment.length - a.segment.length);
    const topSegments = segments.slice(0, 6);

    topSegments.forEach(segment => {
        const pente = calculateSlope(segment.segment);
        const xVals = Array.from({ length: segment.segment.length }, (_, i) => segment.start + i);
        const yVals = segment.segment.map((val, i) => val + pente * (i));

        const color = pente >= 0 ? 'green' : 'red';
        const labelText = `Pente : ${pente.toFixed(2)}`;

        // Ajouter les informations aux tableaux de détails
        const heureDebut = heuresEmg[segment.start];
        const heureFin = heuresEmg[segment.end];

        if (color === 'green') {
            greenDetails.push(`- Début : ${heureDebut}, Fin : ${heureFin}, Pente : ${pente.toFixed(2)}`);
            greenCount++;
        } else if (color === 'red') {
            redDetails.push(`- Début : ${heureDebut}, Fin : ${heureFin}, Pente : ${pente.toFixed(2)}`);
            redCount++;
        }

        datasets.push({
            label: `Segment ${segment.start} à ${segment.end}`,
            data: yVals.map((y, i) => ({ x: xVals[i], y })),
            borderColor: color,
            borderWidth: 1,
            borderDash: [5, 5],
            fill: pente < 0,
            backgroundColor: pente < 0 ? 'rgba(255, 0, 0, 0.05)' : undefined,
            pointRadius: 0
        });
    });

    // Mettre à jour le graphique
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: emgValues.length }, (_, i) => i), // Utiliser les indices pour les labels
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
                }
            }
        }
    });

    // Mettre à jour les informations dans le HTML
    const greenContainer = document.querySelector('.green-container');
    const redContainer = document.querySelector('.red-container');

    if (greenCount > 0) {
        greenContainer.classList.add('show');
        greenContainer.innerHTML = `Nombre de périodes d'augmentation d'activité musculaire : ${greenCount}<br>Détails : <br>${greenDetails.join('<br>')}`;
    } else {
        greenContainer.classList.remove('show');
    }

    if (redCount > 0) {
        redContainer.classList.add('show');
        redContainer.innerHTML = `Nombre de périodes de diminution d'activité musculaire : ${redCount}<br>Détails : <br>${redDetails.join('<br>')}`;
    } else {
        redContainer.classList.remove('show');
    }
}
