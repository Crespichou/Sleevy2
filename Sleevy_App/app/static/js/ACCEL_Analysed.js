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
                const maxCoupures = sessionDurationMinutes;
                const percentage = (coupures.length / maxCoupures) * 100;

                let color;
                if (percentage <= 25) {
                    color = '#d6f4f4';
                } else if (percentage <= 50) {
                    color = 'rgb(248, 250, 162)';
                } else if (percentage <= 85) {
                    color = 'rgb(253, 188, 96)';
                } else {
                    color = 'red';
                }

                gauge.innerHTML = `<div style="width: ${Math.min(percentage, 100)}%; background-color: ${color};"></div>`;
                gaugeLabel.textContent = `Nombre de mouvements parasites : ${coupures.length}`;

                const textContainer = document.querySelector('.text-container');
                coupures.forEach((coupure, index) => {
                    const p = document.createElement('p');
                    p.textContent = `N°${index + 1}: de ${coupure.start.toTimeString().substring(0, 8)} à ${coupure.end.toTimeString().substring(0, 8)}`;
                    textContainer.appendChild(p);
                });

                createAccelChart(valeursAccel, heuresAccel.map(date => date.toTimeString().substring(0, 8)), coupures);
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
        backgroundColor: 'rgba(255, 0, 0, 0.2)',
        borderWidth: 0
    }));

    new Chart(ctxAccel, {
        type: 'line',
        data: {
            labels: heuresAccel,
            datasets: [{
                label: 'Mouvements verticaux de votre bras',
                data: valeursAccel,
                borderColor: 'rgb(21, 0, 253)',
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
                            return index % 5 === 0 ? this.getLabelForValue(value) : '';
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Amplitude de mouvement'
                    }
                }
            }
        }
    });
}
