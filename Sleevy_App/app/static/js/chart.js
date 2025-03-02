document.addEventListener('DOMContentLoaded', function() {
    // Effectuer une requête AJAX pour récupérer les données PPG, EMG et Accel
    fetch('/graphique_ppg_emg')
        .then(response => response.json()) // On s'attend à une réponse au format JSON
        .then(data => {
            if (data && data.ppg_values && data.ppg_values.length > 0 && data.emg_values && data.emg_values.length > 0 && data.accel_values && data.accel_values.length > 0) {
                // Extraire les valeurs et les heures PPG, EMG et Accel de la réponse
                let valeursPpg = data.ppg_values.map(item => item.valeur);
                let heuresPpg = data.ppg_values.map(item => {
                    let heure = item.heure; // Format "YYYY HH"
                    let heurePart = heure.substring(17); // Extrait "HH"
                    return `${heurePart}`; // Ajoute ":00:00.00" pour obtenir "HH:MM:SS.ss"
                });

                let valeursEmg = data.emg_values.map(item => item.valeur);
                let heuresEmg = data.emg_values.map(item => {
                    let heure = item.heure; // Format "YYYY HH"
                    let heurePart = heure.substring(17); // Extrait "HH"
                    return `${heurePart}`; // Ajoute ":00:00.00" pour obtenir "HH:MM:SS.ss"
                });

                let valeursAccel = data.accel_values.map(item => item.valeur);
                let heuresAccel = data.accel_values.map(item => {
                    let heure = item.heure; // Format "YYYY HH"
                    let heurePart = heure.substring(17); // Extrait "HH"
                    return `${heurePart}`; // Ajoute ":00:00.00" pour obtenir "HH:MM:SS.ss"
                });

                // Créer et afficher le graphique PPG
                const ctxPPG = document.getElementById('myChartPPG').getContext('2d');
                new Chart(ctxPPG, {
                    type: 'line', // Choisir le type de graphique (ici, un graphique linéaire)
                    data: {
                        labels: heuresPpg, // Labels des données PPG
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
                                    text: 'Temps'
                                },
                                ticks: {
                                    callback: function(value, index, values) {
                                        // Afficher une heure toutes les 5 valeurs
                                        return index % 2 === 0 ? this.getLabelForValue(value) : '';
                                    }
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
                        labels: heuresEmg, // Labels des données EMG
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
                                    text: 'Temps'
                                },
                                ticks: {
                                    callback: function(value, index, values) {
                                        // Afficher une heure toutes les 5 valeurs
                                        return index % 3 === 0 ? this.getLabelForValue(value) : '';
                                    }
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
                        labels: heuresAccel, // Labels des données Accel
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

            } else {
                console.error('Aucune donnée PPG, EMG ou Accel disponible');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des données PPG, EMG et Accel :', error);
        });
});
