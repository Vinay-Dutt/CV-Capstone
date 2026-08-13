/**
 * Dynamic Chart rendering manager using Chart.js
 */

const ChartManager = {
    radarChart: null,
    barChart: null,
    gaugeChart: null,
    pieChart: null,

    /**
     * Render Complexity Feature Distribution Radar Chart
     */
    renderRadarChart(canvasId, subScores) {
        if (typeof Chart === 'undefined') return;
        const ctx = document.getElementById(canvasId);
        if (!ctx || !subScores) return;

        if (this.radarChart) {
            this.radarChart.destroy();
        }

        this.radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Edge Density', 'Contour Metric', 'GLCM Contrast', 'GLCM Entropy', 'Shannon Entropy', 'Variance'],
                datasets: [{
                    label: 'Normalized Complexity Feature Score',
                    data: [
                        subScores.s_edge || 0,
                        subScores.s_contour || 0,
                        subScores.s_contrast || 0,
                        subScores.s_contrast || 0,
                        subScores.s_entropy || 0,
                        subScores.s_var || 0
                    ],
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    borderColor: '#6366f1',
                    pointBackgroundColor: '#4f46e5',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#4f46e5',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(150, 150, 150, 0.2)' },
                        grid: { color: 'rgba(150, 150, 150, 0.2)' },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: { stepSize: 20 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    /**
     * Render Sub-Domain Decomposition Bar Chart
     */
    renderSubScoreBarChart(canvasId, subScores) {
        if (typeof Chart === 'undefined') return;
        const ctx = document.getElementById(canvasId);
        if (!ctx || !subScores) return;

        if (this.barChart) {
            this.barChart.destroy();
        }

        this.barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Spatial Structure', 'GLCM Texture', 'Info Entropy'],
                datasets: [{
                    label: 'Score (0 - 100)',
                    data: [
                        subScores.spatial_structural || 0,
                        subScores.texture_glcm || 0,
                        subScores.information_entropy || 0
                    ],
                    backgroundColor: ['#6366f1', '#10b981', '#06b6d4'],
                    borderRadius: 8,
                    barThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(150, 150, 150, 0.15)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    /**
     * Render Complexity Gauge Meter
     */
    renderGaugeChart(canvasId, score, colorHex) {
        if (typeof Chart === 'undefined') return;
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.gaugeChart) {
            this.gaugeChart.destroy();
        }

        this.gaugeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Score', 'Remaining'],
                datasets: [{
                    data: [score, Math.max(0, 100 - score)],
                    backgroundColor: [colorHex || '#6366f1', 'rgba(200, 200, 200, 0.2)'],
                    borderWidth: 0,
                    circumference: 240,
                    rotation: 240
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '78%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    },

    /**
     * Render Historical Complexity Distribution Pie Chart
     */
    renderDistributionPieChart(canvasId, distData) {
        if (typeof Chart === 'undefined') return;
        const ctx = document.getElementById(canvasId);
        if (!ctx || !distData) return;

        if (this.pieChart) {
            this.pieChart.destroy();
        }

        const labels = Object.keys(distData);
        const values = Object.values(distData);
        const colors = ['#0dcaf0', '#198754', '#ffc107', '#dc3545', '#6c757d'];

        this.pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
};
