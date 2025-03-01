document.addEventListener('DOMContentLoaded', function() {
    // Effectuer une requête AJAX pour récupérer les données PPG, EMG et Accel
    fetch('/graphique_ppg_emg')
        .then(response => response.json()) // On s'attend à une réponse au format JSON
        .then(data => {
            if (data && data.ppg_values && data.ppg_values.length > 0 && data.emg_values && data.emg_values.length > 0 && data.accel_values && data.accel_values.length > 0) {
                // Extraire les valeurs PPG, EMG et Accel de la réponse
                let valeursPpg = data.ppg_values;
                let valeursEmg = data.emg_values;
                let valeursAccel = data.accel_values;

                // Créer un tableau contenant les labels pour chaque graphique
                // Pour PPG
                const labelsPpg = valeursPpg.map((_, index) => index + 1);  // Labels PPG (indices des valeurs PPG)
                
                // Pour EMG
                const labelsEmg = valeursEmg.map((_, index) => index + 1);  // Labels EMG (indices des valeurs EMG)

                // Pour Accel
                const labelsAccel = valeursAccel.map((_, index) => index + 1);  // Labels Accel (indices des valeurs Accel)

                // Créer et afficher le graphique PPG
                const ctxPPG = document.getElementById('myChartPPG').getContext('2d');
                new Chart(ctxPPG, {
                    type: 'line', // Choisir le type de graphique (ici, un graphique linéaire)
                    data: {
                        labels: labelsPpg, // Labels des données PPG
                        datasets: [{
                            label: 'Valeurs PPG',
                            data: valeursPpg, // Valeurs PPG
                            borderColor: 'rgb(235, 0, 27)', // Couleur de la ligne
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
                                        return 'Valeur PPG: ' + tooltipItem.raw;
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
                                    text: 'Temps (s)'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Valeur PPG'
                                }
                            }
                        }
                    }
                });

                // Créer et afficher le graphique EMG
                const ctxEMG = document.getElementById('myChartEMG').getContext('2d');
                new Chart(ctxEMG, {
                    type: 'line', // Choisir le type de graphique (ici, un graphique linéaire)
                    data: {
                        labels: labelsEmg, // Labels des données EMG
                        datasets: [{
                            label: 'Valeurs EMG',
                            data: valeursEmg, // Valeurs EMG
                            borderColor: 'rgb(0, 123, 255)', // Couleur de la ligne
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
                                        return 'Valeur EMG: ' + tooltipItem.raw;
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
                                    text: 'Temps (s)'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Valeur EMG'
                                }
                            }
                        }
                    }
                });

                // Créer et afficher le graphique Accel
                const ctxAccel = document.getElementById('myChartAccel').getContext('2d');
                new Chart(ctxAccel, {
                    type: 'line', // Choisir le type de graphique (ici, un graphique linéaire)
                    data: {
                        labels: labelsAccel, // Labels des données Accel
                        datasets: [{
                            label: 'Valeurs Accel',
                            data: valeursAccel, // Valeurs Accel
                            borderColor: 'rgb(0, 255, 0)', // Couleur de la ligne
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
                                    text: 'Temps (s)'
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

            } else {
                console.error('Aucune donnée PPG, EMG ou Accel disponible');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données PPG, EMG et Accel :', error);
        });
});
