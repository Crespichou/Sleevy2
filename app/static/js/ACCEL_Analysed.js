document.addEventListener('DOMContentLoaded', function() {
    fetch('/graphique_ppg_emg')
        .then(response => response.json())
        .then(data => {
            if (data.accel_values) {
                const accelValues = data.accel_values;
                console.log('Données Accel :', accelValues);

                let valeursAccel = accelValues.map(item => item.valeur);
                let heuresAccel = accelValues.map(item => new Date(item.heure));

                // Soustraire 1 heure à chaque valeur de temps
                heuresAccel = heuresAccel.map(date => {
                    date.setHours(date.getHours() - 1);
                    return date;
                });

                const startTime = heuresAccel[0];
                const endTime = heuresAccel[heuresAccel.length - 1];
                const sessionDurationMinutes = (endTime - startTime) / 1000 / 60;

                // Arrondir maxCoupures à l'entier le plus proche
                const maxCoupures = Math.round(sessionDurationMinutes);

                // Calculer la moyenne des valeurs d'accélération
                const moyenneAccel = valeursAccel.reduce((sum, value) => sum + value, 0) / valeursAccel.length;
                console.log('Moyenne Accel :', moyenneAccel);

                // Calculer la valeur de référence : moyenne + 225%
                const referenceValue = moyenneAccel + (moyenneAccel * 2.25);
                console.log('Valeur de référence :', referenceValue);

                let coupures = [];
                let i = 1;
                const interval = 10000;

                while (i < valeursAccel.length) {
                    if ((valeursAccel[i - 1] <= referenceValue && valeursAccel[i] > referenceValue) ||
                        (valeursAccel[i - 1] > referenceValue && valeursAccel[i] <= referenceValue)) {
                        let startTime = heuresAccel[i];
                        let nextIndex = i + 1;
                        while (nextIndex < heuresAccel.length && (heuresAccel[nextIndex] - heuresAccel[i]) <= interval) {
                            nextIndex++;
                        }
                        let endTime = heuresAccel[nextIndex - 1];
                        coupures.push({ start: startTime, end: endTime });
                        i = nextIndex;
                    } else {
                        i++;
                    }
                }

                const gauge = document.getElementById('gauge');
                const gaugeLabel = document.getElementById('gauge-label');
                const percentage = (coupures.length / maxCoupures) * 100;

                let color;
                if (percentage <= 25) {
                    color = 'rgb(148, 255, 67)';
                } else if (percentage <= 50) {
                    color = 'rgb(249, 255, 86)';
                } else if (percentage <= 85) {
                    color = 'rgb(255, 173, 58)';
                } else {
                    color = 'red';
                }

                gauge.innerHTML = `<div style="width: ${Math.min(percentage, 100)}%; background-color: ${color};"></div>`;
                gaugeLabel.textContent = `Nombre de mouvements parasites : ${coupures.length}`;

                createAccelChart(valeursAccel, heuresAccel.map(date => date.toTimeString().substring(0, 8)), coupures);

                // Mettre à jour le warn-results-container
                const warnImage = document.getElementById('warn-image');
                const warnText = document.getElementById('warn-text');
                if (coupures.length > maxCoupures / 2) {
                    warnImage.src = "/static/images/warning.png"; // Remplacez par le chemin de votre image
                    warnText.textContent = "Attention, beaucoup de mouvements parasites";
                } else {
                    warnImage.src = "/static/images/valid.png"; // Remplacez par le chemin de votre image
                    warnText.textContent = `${coupures.length}/${maxCoupures}`;
                }
            } else {
                console.error('Aucune donnée Accel trouvée.');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données Accel :', error);
        });
});

function createAccelChart(valeursAccel, heuresAccel, coupures) {
    const ctxAccel = document.getElementById('myChartAccel').getContext('2d');

    let annotations = coupures.map((coupure, index) => ({
        type: 'box',
        xMin: heuresAccel.findIndex(time => time === coupure.start.toTimeString().substring(0, 8)),
        xMax: heuresAccel.findIndex(time => time === coupure.end.toTimeString().substring(0, 8)),
        backgroundColor: 'rgba(247, 181, 0, 0.25)',
        borderWidth: 0,
        label: {
            content: `- N°${index + 1} : de ${coupure.start.toTimeString().substring(0, 8)} à ${coupure.end.toTimeString().substring(0, 8)}`,
            enabled: true,
            position: 'start'
        }
    }));

    const chart = new Chart(ctxAccel, {
        type: 'line',
        data: {
            labels: heuresAccel,
            datasets: [{
                label: 'Mouvements verticaux de votre bras',
                data: valeursAccel,
                borderColor: 'rgb(105, 208, 208)',
                borderWidth: 2,
                fill: false,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function(tooltipItem) {
                            return 'Valeur Accel: ' + tooltipItem.raw;
                        }
                    }
                },
                annotation: {
                    annotations: annotations
                }
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Temps'
                    },
                    ticks: {
                        callback: function(value, index) {
                            return index % 1 === 0 ? this.getLabelForValue(value) : '';
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Amplitude de mouvement'
                    },
                    grid:{
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1,
                        borderDash: [10, 15],
                        drawTicks: false
                    }
                }
            }
        }
    });

    // Initialiser le texte par défaut
    const textContainer = document.querySelector('.text-container');
    textContainer.innerHTML = '<p>Passez la souris sur une zone orange pour voir les détails des mouvements parasites.</p>';

    // Ajouter un écouteur d'événements pour le survol de la souris
    ctxAccel.canvas.addEventListener('mousemove', function(event) {
        const mouseX = event.offsetX;
        const mouseY = event.offsetY;

        // Trouver l'annotation la plus proche
        const nearestAnnotation = annotations.find(annotation => {
            const xMin = chart.scales.x.getPixelForValue(annotation.xMin);
            const xMax = chart.scales.x.getPixelForValue(annotation.xMax);
            return mouseX >= xMin && mouseX <= xMax;
        });

        if (nearestAnnotation) {
            const coupure = coupures[annotations.indexOf(nearestAnnotation)];
            const durationSeconds = Math.round((coupure.end - coupure.start) / 1000);
            textContainer.innerHTML = `<p>Il s'agit de votre mouvement parasite numéro ${annotations.indexOf(nearestAnnotation) + 1}. Il démarre à ${coupure.start.toTimeString().substring(0, 8)} et se termine à ${coupure.end.toTimeString().substring(0, 8)}. Il dure au total ${durationSeconds} secondes.</p>`;
        } else {
            // Réinitialiser le texte par défaut si la souris n'est pas sur une annotation
            textContainer.innerHTML = '<p>Passez la souris sur une zone orange pour voir les détails des mouvements parasites.</p>';
        }
    });
}
