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
                    return heure.substring(17); // Extrait "HH:MM:SS"
                });

                // Créer le graphique avec les données Accel
                createAccelChart(valeursAccel, heuresAccel);
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
