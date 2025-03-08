document.addEventListener('DOMContentLoaded', function() {
    // Effectuer une requête AJAX pour récupérer les données PPG, EMG et Accel
    fetch('/graphique_ppg_emg')
        .then(response => response.json()) // On s'attend à une réponse au format JSON
        .then(data => {
            if (data && data.ppg_values && data.ppg_values.length > 0 && data.emg_values && data.emg_values.length > 0 && data.accel_values && data.accel_values.length > 0) {
                // Extraire les valeurs et les heures PPG, EMG et Accel de la réponse
                let valeursPpg = data.ppg_values.map(item => item.valeur);
                let heuresPpg = data.ppg_values.map(item => new Date(item.heure));

                let valeursEmg = data.emg_values.map(item => item.valeur);
                let heuresEmg = data.emg_values.map(item => new Date(item.heure));

                let valeursAccel = data.accel_values.map(item => item.valeur);
                let heuresAccel = data.accel_values.map(item => new Date(item.heure));

                // Fonction pour formater les heures en HH:MM:SS en soustrayant 1 heure
                function formatTime(date) {
                    date.setHours(date.getHours() - 1); // Soustraire 1 heure
                    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                }

                let labelsPpg = heuresPpg.map(formatTime);
                let labelsEmg = heuresEmg.map(formatTime);
                let labelsAccel = heuresAccel.map(formatTime);

                // Créer et afficher le graphique PPG
                const ctxPPG = document.getElementById('myChartPPG').getContext('2d');
                new Chart(ctxPPG, {
                    type: 'line',
                    data: {
                        labels: labelsPpg,
                        datasets: [{
                            label: 'Rythme cardiaque',
                            data: valeursPpg,
                            borderColor: 'rgb(154, 2, 19)',
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Temps' } },
                            y: { title: { display: true, text: 'Valeur PPG' } }
                        }
                    }
                });

                // Créer et afficher le graphique EMG
                const ctxEMG = document.getElementById('myChartEMG').getContext('2d');
                new Chart(ctxEMG, {
                    type: 'line',
                    data: {
                        labels: labelsEmg,
                        datasets: [{
                            label: 'Activité musculaire',
                            data: valeursEmg,
                            borderColor: 'rgb(0, 90, 186)',
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Temps' } },
                            y: { title: { display: true, text: 'Valeur EMG' } }
                        }
                    }
                });

                // Créer et afficher le graphique Accel
                const ctxAccel = document.getElementById('myChartAccel').getContext('2d');
                new Chart(ctxAccel, {
                    type: 'line',
                    data: {
                        labels: labelsAccel,
                        datasets: [{
                            label: 'Mouvements du bras',
                            data: valeursAccel,
                            borderColor: 'rgb(0, 132, 0)',
                            borderWidth: 2,
                            fill: false,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Temps' } },
                            y: { title: { display: true, text: 'Valeur Accel' } }
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
