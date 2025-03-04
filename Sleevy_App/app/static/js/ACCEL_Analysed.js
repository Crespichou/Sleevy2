document.addEventListener('DOMContentLoaded', function() {
    fetch('/graphique_ppg_emg')
        .then(response => response.json())
        .then(data => {
            if (data.accel_values) {
                const accelValues = data.accel_values;
                console.log('Données Accel :', accelValues);

                // Extraire les valeurs et les heures Accel
                let valeursAccel = accelValues.map(item => item.valeur);
                let heuresAccel = accelValues.map(item => {
                    let heure = item.heure; // Format "YYYY-MM-DD HH:MM:SS"
                    return new Date(heure); // Convertir en objet Date pour les comparaisons
                });

                // Calculer la durée totale de la session en minutes
                const startTime = heuresAccel[0];
                const endTime = heuresAccel[heuresAccel.length - 1];
                const sessionDurationMinutes = (endTime - startTime) / 1000 / 60; // Durée en minutes

                // Créer le graphique avec les données Accel
                createAccelChart(valeursAccel, heuresAccel.map(date => date.toTimeString().substring(0, 8)));

                // Compter le nombre de fois où la ligne à 0.45 est coupée, en regroupant les coupures dans un intervalle de 10 secondes
                let coupures = [];
                let i = 1;
                const interval = 10000; // 10 secondes en millisecondes

                while (i < valeursAccel.length) {
                    if ((valeursAccel[i - 1] <= 0.3 && valeursAccel[i] > 0.3) ||
                        (valeursAccel[i - 1] > 0.3 && valeursAccel[i] <= 0.3)) {

                        let startTime = heuresAccel[i];
                        // Avancer de 10 secondes ou jusqu'à la fin des données
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

                // Afficher le nombre total de coupures dans le info-container
                const infoContainer = document.querySelector('.info-container-accel');
                const textContainer = document.querySelector('.text-container');

                // Mettre à jour la jauge
                const gauge = document.getElementById('gauge');
                const gaugeLabel = document.getElementById('gauge-label');
                const maxCoupures = sessionDurationMinutes; // Nombre maximal de coupures autorisées
                const percentage = (coupures.length / maxCoupures) * 100; // Calcul du pourcentage par rapport au maximum

                // Définir les couleurs pour chaque plage de pourcentage
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
                gaugeLabel.textContent = `Nombre de mouvements parasites : ${coupures.length} `;

                // Afficher les intervalles de coupures dans le text-container
                coupures.forEach((coupure, index) => {
                    const p = document.createElement('p');
                    p.textContent = `N°${index + 1}: de ${coupure.start.toTimeString().substring(0, 8)} à ${coupure.end.toTimeString().substring(0, 8)}`;
                    textContainer.appendChild(p);
                });
            } else {
                console.error('Aucune donnée Accel trouvée.');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données Accel :', error);
        });
});

function createAccelChart(valeursAccel, heuresAccel) {
    const ctxAccel = document.getElementById('myChartAccel').getContext('2d');
    new Chart(ctxAccel, {
        type: 'line', // Choisir le type de graphique (ici, un graphique linéaire)
        data: {
            labels: heuresAccel, // Labels des données Accel
            datasets: [{
                label: 'Valeurs Accélèromètre',
                data: valeursAccel, // Valeurs Accel
                borderColor: 'rgb(21, 0, 253)', // Couleur de la ligne
                borderWidth: 2,
                fill: false, // Ne pas remplir l'aire sous la courbe
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    enabled: true, // Activer les tooltips
                    callbacks: {
                        label: function(tooltipItem) {
                            return 'Valeur Accel: ' + tooltipItem.raw;
                        }
                    }
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
                        callback: function(value, index, values) {
                            // Afficher une heure toutes les 5 valeurs
                            return index % 5 === 0 ? this.getLabelForValue(value) : '';
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Valeur Accel'
                    }
                }
            }
        }
    });
}
