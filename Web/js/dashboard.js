document.addEventListener('DOMContentLoaded', function () {
    updateGreeting(); // Set personalized greeting
    fetchLiveUSDMXN(); // Fetch real-time FX rate
    fetch('data/dashboard_data.json')
        .then(response => response.json())
        .then(data => {
            window.dashboardData = data; // Store globally for Modal access
            updateMeta(data.metadata);
            // Strategies
            renderCarryBox(data.system_status);
            renderInflationBox(data.inflation);
            renderRiskBox(data.risk);

            // Click Listeners for each box
            document.getElementById('box-carry').onclick = () => openAlphaModal('carry');
            document.getElementById('box-inflation').onclick = () => openAlphaModal('inflation');
            document.getElementById('box-risk').onclick = () => openAlphaModal('risk');

            renderPillar1(data.carry_trade);
            renderPillar2(data.inflation);
            renderPillar3(data.risk);
            renderPillar4(data.economy);

            // Render US Stocks Radar
            if (data.us_stocks) {
                renderUSStocks(data.us_stocks);
            }

            // Render Global Indicators
            if (data.global_indicators) {
                renderGlobalIndicators(data.global_indicators);
            }

            // Close tooltips when clicking outside
            document.addEventListener('click', function (e) {
                if (!e.target.closest('.tooltip-icon')) {
                    document.querySelectorAll('.tooltip-icon').forEach(t => t.blur());
                }
            });
        })
        .catch(err => console.error("Error loading data:", err));
});

// Fetch live USD/MXN rate from real-time APIs
function fetchLiveUSDMXN() {
    // Live rate is now fetched by Python backend and stored in metadata.live_fx_rate
    // The display will be updated in updateMeta() when JSON loads
    console.log('Live FX rate will be loaded from backend JSON');
}

function updateLiveFXDisplay(livePrice) {
    // Update the main display with LIVE rate
    const liveEl = document.getElementById('val-fix');
    if (liveEl && livePrice) {
        liveEl.textContent = `$ ${livePrice.toFixed(4)}`;
        liveEl.title = 'Precio EN VIVO';
        liveEl.style.color = '#00ff88'; // Green = live
    }
    window.liveFXRate = livePrice;
    console.log('Live USD/MXN:', livePrice);
}

// ... (keep updateGreeting) ...

// --- MODAL LOGIC (DEEP DIVE) ---
function renderCarryBox(status) {
    if (!status) return;
    const box = document.getElementById('box-carry');
    const statEl = document.getElementById('carry-status');

    // Map status specifically for the short card
    let displayStatus = "NEUTRAL";
    let colorVar = "var(--accent-orange)";

    if (status.status.includes("RIESGO ALTO") || status.status.includes("ROJO")) {
        displayStatus = "RIESGO ALTO";
        colorVar = "var(--accent-red)";
    } else if (status.status.includes("RIESGO ACEPTABLE") || status.status.includes("VERDE")) {
        displayStatus = "RIESGO BAJO";
        colorVar = "var(--accent-green)";
    }

    statEl.textContent = displayStatus;
    statEl.style.color = colorVar;
    box.style.borderColor = colorVar;

    document.getElementById('carry-action').textContent = status.action;
    document.getElementById('carry-prob').textContent = status.probability;
    document.getElementById('carry-sl').textContent = status.stop_loss;
    document.getElementById('carry-reason').textContent = status.reason;
}

function renderInflationBox(inflData) {
    if (!inflData || !inflData[0]) return;
    const data = inflData.slice(-1)[0]; // get latest (Fix: was [0])
    const realRate = parseFloat(data['Real Rate Ex-Post'] || 0);

    const box = document.getElementById('box-inflation');
    const statEl = document.getElementById('inf-status');
    const actionEl = document.getElementById('inf-action');
    const levelEl = document.getElementById('inf-real');

    levelEl.textContent = realRate.toFixed(2) + "%";

    if (realRate > 0) {
        statEl.textContent = "SUPERÁVIT REAL";
        statEl.style.color = "var(--accent-green)";
        box.style.borderColor = "var(--accent-green)";
        actionEl.textContent = "MANTENER (QUEDATE EN CETES)";
    } else {
        statEl.textContent = "EROSIÓN CAPITAL";
        statEl.style.color = "var(--accent-red)";
        box.style.borderColor = "var(--accent-red)";
        actionEl.textContent = "HEDGE EN UDIS";
    }
}

function renderRiskBox(riskData) {
    if (!riskData || !riskData[0]) return;
    const data = riskData.slice(-1)[0];
    const close = parseFloat(data['Close'] || data['Tipo de Cambio FIX']);
    const upper = parseFloat(data['Upper_Band']);
    const isOverbought = close >= (upper * 0.995);

    const box = document.getElementById('box-risk');
    const statEl = document.getElementById('risk-status');
    const actionEl = document.getElementById('risk-action');
    const levelEl = document.getElementById('risk-level');

    levelEl.textContent = isOverbought ? "SOBRECOMPRA (>2σ)" : "RANGO NORMAL";

    if (isOverbought) {
        statEl.textContent = "PRECIO INFLADO";
        statEl.style.color = "var(--accent-red)";
        box.style.borderColor = "var(--accent-red)";
        actionEl.textContent = "NO COMPRAR USD (ESPERAR)";
    } else {
        statEl.textContent = "ESTABILIDAD";
        statEl.style.color = "var(--accent-green)";
        box.style.borderColor = "var(--accent-green)";
        actionEl.textContent = "EJECUTAR ORDEN (COMPRA DOLARES)";
    }
}

function openAlphaModal(strategyType) {
    if (!window.dashboardData) return;

    // Common Data
    const carryData = window.dashboardData.carry_trade.slice(-1)[0];
    const currentSpread = parseFloat(carryData['Carry Spread (bp)']).toFixed(0);
    const mxRate = parseFloat(carryData['TIIE 28d']).toFixed(2);
    const usRate = parseFloat(carryData['FED Rate (Proxy 13W)'] || carryData['3-Month Bill'] || 0).toFixed(2);
    const status = window.dashboardData.system_status ? window.dashboardData.system_status.status : "";

    const modal = document.getElementById('logic-modal');
    const body = document.getElementById('modal-body');
    const title = document.getElementById('modal-title');

    let contentHtml = "";

    // SWITCH CONTENT BASED ON CLICKED BOX
    if (strategyType === 'carry') {
        title.textContent = "ANÁLISIS: CARRY TRADE";

        // Get additional data for explanations
        const riskData = window.dashboardData.risk ? window.dashboardData.risk.slice(-1)[0] : {};
        const systemStatus = window.dashboardData.system_status || {};
        const currentPrice = parseFloat(riskData['Close'] || 18).toFixed(2);
        const stopLoss = systemStatus.stop_loss || '$' + (currentPrice * 0.99).toFixed(2);
        const probability = systemStatus.probability || '50%';
        const volZ = parseFloat(riskData['Vol_Z_Score'] || 0).toFixed(1);

        // Calculate spread percentage for explanation
        const spreadPct = (mxRate - usRate).toFixed(2);

        // REUSE LOGIC SECTIONS (1, 2, 3 + Verdict)
        contentHtml += `
        <div class="logic-section" onclick="toggleSection(this)">
            <div class="accordion-header"><h4>1. DATOS BASE</h4><span class="accordion-icon">▼</span></div>
            <div class="accordion-content"><p class="logic-text">• Tasa México (TIIE 28d): ${mxRate}%<br>• Tasa EE.UU. (T-Bill 13sem): ${usRate}%<br>• USD/MXN: $${currentPrice}<br>• Volatilidad (Z-Score): ${volZ}</p></div>
        </div>
        <div class="logic-section" onclick="toggleSection(this)">
            <div class="accordion-header"><h4>2. CÁLCULO DEL SPREAD</h4><span class="accordion-icon">▼</span></div>
            <div class="accordion-content">
                <p class="logic-text">
                    <strong>Fórmula:</strong><br>
                    Spread = Tasa México - Tasa EE.UU.<br><br>
                    <strong>Cálculo:</strong><br>
                    ${mxRate}% - ${usRate}% = <strong>${spreadPct}%</strong><br><br>
                    <strong>Conversión a Puntos Base (bps):</strong><br>
                    1 punto porcentual = 100 puntos base<br>
                    ${spreadPct}% × 100 = <strong>${currentSpread} bps</strong><br><br>
                    Este spread de ${spreadPct}% (${currentSpread} bps) representa el premio por invertir en pesos mexicanos en lugar de dólares.
                </p>
            </div>
        </div>
        <div class="logic-section" onclick="toggleSection(this)">
            <div class="accordion-header"><h4>3. CÁLCULO DE PROBABILIDAD</h4><span class="accordion-icon">▼</span></div>
            <div class="accordion-content">
                <p class="logic-text">
                    La probabilidad se basa en dos factores:<br><br>
                    <strong>Factor 1: Nivel del Spread</strong><br>
                    • Spread > 500 bps: Alta probabilidad de éxito (68%+)<br>
                    • Spread 400-500 bps: Zona neutral (55%)<br>
                    • Spread < 400 bps: Mayor riesgo (75% de que el peso se devalúe)<br><br>
                    <strong>Factor 2: Volatilidad (Z-Score)</strong><br>
                    • Z < 1.5: Mercado tranquilo, mayor confianza<br>
                    • Z > 2.0: Mercado volátil, mayor riesgo<br><br>
                    <strong>Tu situación actual:</strong><br>
                    Spread: ${currentSpread} bps | Volatilidad Z: ${volZ}<br>
                    Probabilidad estimada: <strong>${probability}</strong>
                </p>
            </div>
        </div>
        <div class="logic-section" onclick="toggleSection(this)">
            <div class="accordion-header"><h4>4. CÁLCULO DEL STOP LOSS</h4><span class="accordion-icon">▼</span></div>
            <div class="accordion-content">
                <p class="logic-text">
                    El Stop Loss es un nivel de emergencia para limitar pérdidas.<br><br>
                    <strong>Fórmula:</strong><br>
                    <code>Stop Loss = Precio Actual × 0.99</code><br>
                    <code>Stop Loss = $${currentPrice} × 0.99 = ${stopLoss}</code><br><br>
                    <strong>Significado:</strong><br>
                    Si el precio del dólar baja a ${stopLoss}, deberías cerrar tu posición y aceptar una pérdida pequeña (~1%) en lugar de arriesgarte a perder más.<br><br>
                    <strong>Ejemplo práctico:</strong><br>
                    • Compras dólares a $${currentPrice}<br>
                    • El dólar baja a ${stopLoss}<br>
                    • Vendes y pierdes solo ~1%<br>
                    • Sin Stop Loss, podrías perder 5-10% si baja más
                </p>
            </div>
        </div>
        `;

        // VERDICT ONLY
        if (status.includes("RIESGO ALTO") || status.includes("ROJO")) {
            contentHtml += `<div class="logic-section active" onclick="toggleSection(this)"><div class="accordion-header"><h4 class="highlight-red">5. DICTAMEN: SHORT MXN</h4><span class="accordion-icon">▲</span></div><div class="accordion-content"><p class="logic-text">Spread bajo (< 400bps). Riesgo alto de devaluación. <strong>Recomendación: Compra dólares con Stop Loss en ${stopLoss}</strong></p></div></div>`;
        } else if (status.includes("RIESGO ACEPTABLE") || status.includes("VERDE")) {
            contentHtml += `<div class="logic-section active" onclick="toggleSection(this)"><div class="accordion-header"><h4 class="highlight-green">5. DICTAMEN: LONG MXN</h4><span class="accordion-icon">▲</span></div><div class="accordion-content"><p class="logic-text">Spread alto (> 500bps). Ganancia segura. <strong>Recomendación: Mantén pesos, aprovecha las tasas altas.</strong></p></div></div>`;
        } else {
            contentHtml += `<div class="logic-section active" onclick="toggleSection(this)"><div class="accordion-header"><h4 style="color:var(--accent-orange)">5. DICTAMEN: NEUTRAL</h4><span class="accordion-icon">▲</span></div><div class="accordion-content"><p class="logic-text">Zona gris. Precaución recomendada.</p></div></div>`;
        }

    } else if (strategyType === 'inflation') {
        title.textContent = "ANÁLISIS: ESCUDO DE INFLACIÓN";
        const infl = window.dashboardData.inflation.slice(-1)[0];
        const nominalRate = parseFloat(infl['Cetes 28d'] || 0).toFixed(2);
        const inflationRate = parseFloat(infl['Inflation YoY'] || 0).toFixed(2);
        const real = parseFloat(infl['Real Rate Ex-Post']).toFixed(2);

        contentHtml += `
            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>1. DATOS (MATERIA PRIMA)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        Comparamos lo que te paga el banco vs. lo que suben los precios:<br><br>
                        • <strong>Tasa Rendimiento (Cetes/Bonos):</strong> ${nominalRate}% (Fuente: Banxico)<br>
                        • <strong>Inflación Anual (INPC):</strong> ${inflationRate}% (Fuente: INEGI)<br>
                        Para ganar dinero real, tu tasa debe ser mayor a la inflación.
                    </p>
                </div>
            </div>

            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>2. EL CÁLCULO (TASA REAL)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        Restamos la inflación a tu ganancia bruta:<br><br>
                        <code>${nominalRate}% (Ganancia) - ${inflationRate}% (Costo Vida) = ${real}%</code><br><br>
                        Este <strong>${real}%</strong> es tu verdadero crecimiento de riqueza (Poder Adquisitivo).
                    </p>
                </div>
            </div>

            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>3. REGLAS (UMBRALES DE RIQUEZA)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        <strong>> 1.0% (VERDE):</strong> Creación de Riqueza. Estás venciendo al sistema.<br>
                        <strong>0% a 1% (AMARILLO):</strong> Tablas. Solo mantienes el valor, no ganas.<br>
                        <strong>< 0% (ROJO):</strong> Erosión. Tu dinero vale menos cada día aunque genere intereses.
                    </p>
                </div>
            </div>

            <div class="logic-section active" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4 class="${real > 0 ? 'highlight-green' : 'highlight-red'}">4. DICTAMEN: ${real > 0 ? 'SUPERÁVIT REAL' : 'EROSIÓN DE CAPITAL'}</h4>
                    <span class="accordion-icon">▲</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        <strong>Conclusión:</strong> Tu Tasa Real es <strong>${real}%</strong>.
                        ${real > 0 ? 'Estás ganándole la carrera a los precios.' : 'La inflación está destruyendo el valor de tu dinero.'}<br><br>
                        <strong>INSTRUCCIÓN CLARA:</strong><br>
                        ${real > 0 ?
                '✅ <strong>REINVERTIR (Interés Compuesto):</strong> Quédate en Cetes/Bonddia. Tu estrategia actual funciona. Solo asegúrate de reinvertir las ganancias mes a mes.' :
                '🛡️ <strong>HEDGE EN UDIS (Blindaje):</strong> Mueve tu capital a <strong>UDIBONOS</strong>. Estos instrumentos pagan una tasa fija + la inflación, garantizando que NUNCA pierdas poder de compra.'}
                    </p>
                </div>
            </div>
        `;

    } else if (strategyType === 'risk') {
        title.textContent = "ANÁLISIS: TERMÓMETRO DE RIESGO";
        const risk = window.dashboardData.risk.slice(-1)[0];
        const close = parseFloat(risk['Close'] || risk['Tipo de Cambio FIX']).toFixed(2);
        const upper = parseFloat(risk['Upper_Band']).toFixed(2);
        const lower = parseFloat(risk['Lower_Band']).toFixed(2);
        const sma = parseFloat(risk['SMA_20']).toFixed(2);
        const isPanic = parseFloat(close) >= (parseFloat(upper) * 0.995);

        contentHtml += `
            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>1. DATOS (ESTADÍSTICA)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        Analizamos la volatilidad con <strong>Bandas de Bollinger (20, 2)</strong>:<br><br>
                        • <strong>Precio Actual:</strong> $${close}<br>
                        • <strong>Precio Justo (Promedio):</strong> $${sma}<br>
                        • <strong>Techo de Pánico:</strong> $${upper}
                    </p>
                </div>
            </div>

            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>2. EL CÁLCULO (DESVIACIÓN)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        Medimos la "temperatura" del mercado. Si el precio toca el techo, es fiebre (miedo). Si está en medio, es temperatura ambiente (normalidad).
                    </p>
                </div>
            </div>

            <div class="logic-section" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4>3. REGLAS (PSICOLOGÍA)</h4>
                    <span class="accordion-icon">▼</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        <strong>Sobrecompra (ROJO):</strong> Todo el mundo está comprando por miedo. El precio está inflado artificialmente.<br>
                        <strong>Estabilidad (VERDE):</strong> Flujo normal de oferta y demanda. Precio justo.
                    </p>
                </div>
            </div>

            <div class="logic-section active" onclick="toggleSection(this)">
                <div class="accordion-header">
                    <h4 class="${isPanic ? 'highlight-red' : 'highlight-green'}">4. DICTAMEN: ${isPanic ? 'PRECIO INFLADO (PÁNICO)' : 'ESTABILIDAD'}</h4>
                    <span class="accordion-icon">▲</span>
                </div>
                <div class="accordion-content">
                    <p class="logic-text">
                        <strong>Diagnóstico:</strong> ${isPanic ? 'El precio tocó el techo estadístico. Está "caro" por miedo irracional.' : 'El precio es justo y estable.'}<br><br>
                        <strong>INSTRUCCIÓN CLARA:</strong><br>
                        ${isPanic ?
                '✋ <strong>PAUSAR COMPRAS:</strong> No compres dólares hoy. El precio está inflado. Espera unos días a que baje hacia su promedio ($' + sma + ') para comprar más barato.' :
                '🛒 <strong>EJECUTAR ORDEN:</strong> Si necesitas dólares para pagar proveedores o deuda, cómpralos YA. El mercado está tranquilo y el precio es justo.'}
                    </p>
                </div>
            </div>
        `;
    }

    body.innerHTML = contentHtml;
    modal.style.display = "flex";

    document.querySelector('.close-modal').onclick = () => modal.style.display = "none";
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };
}

// Helper to toggle accordion
window.toggleSection = function (element) {
    // Optional: Close others? For now, independent toggles are better UX
    element.classList.toggle("active");

    // Rotate Icon
    const icon = element.querySelector('.accordion-icon');
    if (element.classList.contains('active')) {
        icon.textContent = "▲";
    } else {
        icon.textContent = "▼";
    }
}

function updateGreeting() {
    const hour = new Date().getHours();
    const title = document.getElementById('main-title');
    let greeting = "BUENOS DÍAS";

    if (hour >= 12 && hour < 19) {
        greeting = "BUENAS TARDES";
    } else if (hour >= 19 || hour < 5) {
        greeting = "BUENAS NOCHES";
    }

    title.textContent = `${greeting} ALEJANDRO`;
}


function updateMeta(meta) {
    if (meta && meta.generated_at) {
        document.getElementById('last-update').textContent = `Actualizado: ${meta.generated_at}`;
    }
    // Display live FX rate from backend
    if (meta && meta.live_fx_rate) {
        updateLiveFXDisplay(meta.live_fx_rate);
    }
}

// --- ALPHA BOX ---
// Global state for status
let currentAlphaStatus = null;

// --- ALPHA BOX ---
function renderAlphaBox(status) {
    if (!status) return;
    currentAlphaStatus = status; // Store for modal

    const box = document.getElementById('alpha-box');
    const statEl = document.getElementById('alpha-status');

    statEl.textContent = status.status;
    document.getElementById('alpha-action').textContent = status.action;
    document.getElementById('alpha-prob').textContent = status.probability;
    document.getElementById('alpha-sl').textContent = status.stop_loss;
    document.getElementById('alpha-reason').textContent = status.reason;

    // Color Logic
    let themeColor = "var(--accent-orange)";
    if (status.status.includes("RIESGO ACEPTABLE") || status.status.includes("VERDE")) {
        box.style.borderColor = "var(--accent-green)";
        statEl.style.color = "var(--accent-green)";
        themeColor = "var(--accent-green)";
    } else if (status.status.includes("RIESGO ALTO") || status.status.includes("ROJO")) {
        box.style.borderColor = "var(--accent-red)";
        statEl.style.color = "var(--accent-red)";
        themeColor = "var(--accent-red)";
    } else {
        box.style.borderColor = "var(--accent-orange)";
        statEl.style.color = "var(--accent-orange)";
    }

    // Add Click Listener (Once)
    if (!box.dataset.hasListener) {
        box.addEventListener('click', openAlphaModal);
        box.dataset.hasListener = "true";
    }
}

// --- PILLAR 1: CARRY TRADE (Logic: Spread Zones) ---
function renderPillar1(data) {
    if (!data || data.length === 0) return;
    const last = data[data.length - 1];

    // KPI
    document.getElementById('val-tiie').textContent = `${parseFloat(last['TIIE 28d']).toFixed(2)}%`;
    const spread = parseFloat(last['Carry Spread (bp)']);
    const spreadEl = document.getElementById('sub-spread');
    spreadEl.textContent = `Spread: ${spread.toFixed(0)} bp`;

    // Logic: Green if > 500, Red/Yellow if < 400
    const badge = document.getElementById('badge-carry');
    let spreadColor = '#636EFA'; // Default

    if (spread > 500) {
        badge.textContent = "ZONA COMPRA (AGRESIVA)";
        badge.className = "badge success";
        spreadEl.style.color = "var(--accent-green)";
        spreadColor = "#34c759"; // Green
    } else if (spread < 400) {
        badge.textContent = "ALERTA SALIDA";
        badge.className = "badge danger";
        spreadEl.style.color = "var(--accent-red)";
        spreadColor = "#ff3b30"; // Red
    } else {
        badge.textContent = "NEUTRAL";
        badge.className = "badge warning";
        spreadColor = "#ff9500"; // Orange
    }

    // Chart
    const ctx = document.getElementById('chartCarry').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.Date),
            datasets: [{
                label: 'Spread BP',
                data: data.map(d => d['Carry Spread (bp)']),
                borderColor: spreadColor,
                backgroundColor: spreadColor === "#34c759" ? 'rgba(52, 199, 89, 0.1)' : 'rgba(255, 59, 48, 0.1)',
                fill: true,
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: getChartOptions()
    });
}

// --- PILLAR 2: INFLATION ---
function renderPillar2(data) {
    if (!data || data.length === 0) return;
    const last = data[data.length - 1];

    // KPI
    // Prefer Real Rate if available, else Breakeven
    let val = '--';
    if (last['Real Rate Ex-Post']) {
        val = parseFloat(last['Real Rate Ex-Post']).toFixed(2);
        document.getElementById('val-be').textContent = `${val}%`;
    } else { // Fallback
        val = parseFloat(last['Breakeven Inflation']).toFixed(2);
        document.getElementById('val-be').textContent = `${val}%`;
    }

    // Chart
    const ctx = document.getElementById('chartInflation').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.Date),
            datasets: [{
                label: 'Tasa Real Ex-Post',
                data: data.map(d => d['Real Rate Ex-Post'] || d['Breakeven Inflation']),
                borderColor: '#FF6692',
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: getChartOptions()
    });
}

// --- PILLAR 3: RISK (Logic: Bollinger Alerts) ---
// Store chart instance and data globally for period switching
let riskChart = null;
let riskData = [];

function renderPillar3(data) {
    if (!data || data.length === 0) return;

    // Store data globally for period switching
    riskData = data;
    const last = data[data.length - 1];

    // KPI - Only update if no live rate is available
    const close = parseFloat(last['Close'] || last['Tipo de Cambio FIX']);
    if (!window.liveFXRate) {
        document.getElementById('val-fix').textContent = `$ ${close.toFixed(2)}`;
    }
    const vol = parseFloat(last['Vol_Z_Score'] || 0);
    const upper = parseFloat(last['Upper_Band'] || 999);
    const bandWidth = parseFloat(last['Band_Width'] || 0.1);

    // Charts.js doesn't do Candles easily. We will show Close price + Bands as simple lines.

    const badge = document.getElementById('badge-risk');

    // Logic: Price touches Upper Band -> SOBRECOMPRA
    // Logic: Low Vol -> EXPLOSION

    if (close >= upper * 0.995) { // Near or above upper band
        badge.textContent = "ALERTA: SOBRECOMPRA";
        badge.className = "badge danger";
    } else if (bandWidth < 0.05) { // Very tight bands (squeeze)
        badge.textContent = "ALERTA: EXPLOSIÓN INMINENTE";
        badge.className = "badge warning";
    } else {
        badge.textContent = "NORMAL";
        badge.className = "badge success";
    }

    // Render chart with default 90 days
    renderRiskChart(data.slice(-90));
}

function renderRiskChart(data) {
    const ctx = document.getElementById('chartRisk').getContext('2d');

    // Destroy existing chart if any
    if (riskChart) {
        riskChart.destroy();
    }

    riskChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.Date),
            datasets: [
                {
                    label: 'USD/MXN',
                    data: data.map(d => d['Close'] || d['Tipo de Cambio FIX']),
                    borderColor: '#00CC96',
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Upper',
                    data: data.map(d => d['Upper_Band']),
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    pointRadius: 0,
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: 'Lower',
                    data: data.map(d => d['Lower_Band']),
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    pointRadius: 0,
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        },
        options: getChartOptions()
    });
}

function setChartPeriod(days) {
    // Update active button
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.remove('active');
        if (parseInt(btn.dataset.period) === days) {
            btn.classList.add('active');
        }
    });

    // Filter data and re-render
    if (riskData.length > 0) {
        const filteredData = riskData.slice(-days);
        renderRiskChart(filteredData);
    }
}

// --- PILLAR 4: ECONOMY ---
function renderPillar4(data) {
    if (!data || data.length === 0) return;
    const last = data[data.length - 1];

    // KPI
    // Just display something relevant
    if (last['Divergence']) {
        document.getElementById('val-div').textContent = parseFloat(last['Divergence']).toFixed(1);
    }

    // Chart
    const ctx = document.getElementById('chartEconomy').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.Date),
            datasets: [{
                label: 'M1 (Dinero)',
                data: data.map(d => d['M1 Normalized']),
                borderColor: '#636EFA',
                borderWidth: 2,
                pointRadius: 0
            },
            {
                label: 'IPC (Bolsa)',
                data: data.map(d => d['IPC Normalized']),
                borderColor: '#00CC96',
                borderWidth: 2,
                pointRadius: 0
            }]
        },
        options: getChartOptions()
    });
}

function getChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                labels: { color: '#888' }
            }
        },
        scales: {
            x: {
                type: 'time',
                time: { unit: 'month' },
                grid: { display: false },
                ticks: { color: '#555' }
            },
            y: {
                grid: { color: '#222' },
                ticks: { color: '#555' }
            }
        }
    };
}

// --- US STOCKS RADAR ---
function renderUSStocks(stocks) {
    const container = document.getElementById('stocks-container');
    if (!container || !stocks || stocks.length === 0) return;

    // Clear loading message
    container.innerHTML = '';

    stocks.forEach((stock, index) => {
        const changeClass = stock.change_pct >= 0 ? 'positive' : 'negative';
        const changeSign = stock.change_pct >= 0 ? '+' : '';

        // Map signal to CSS class
        let signalClass = 'mantener';
        if (stock.signal === 'COMPRAR') signalClass = 'comprar';
        else if (stock.signal === 'VENDER') signalClass = 'vender';
        else if (stock.signal === 'SOBRECOMPRA') signalClass = 'sobrecompra';
        else if (stock.signal === 'SOBREVENTA') signalClass = 'sobreventa';

        const card = document.createElement('div');
        card.className = 'stock-card';
        card.innerHTML = `
            <div class="stock-header">
                <div>
                    <div class="stock-ticker">${stock.ticker}</div>
                    <div class="stock-name">${stock.name}</div>
                </div>
            </div>
            <div class="stock-sparkline">
                <canvas id="sparkline-${stock.ticker}" width="100" height="30"></canvas>
            </div>
            <div class="stock-price">$${stock.price.toFixed(2)}</div>
            <div class="stock-change ${changeClass}">
                ${changeSign}${stock.change.toFixed(2)} (${changeSign}${stock.change_pct.toFixed(2)}%)
            </div>
            <div class="stock-indicators">
                <span class="stock-rsi">RSI: ${stock.rsi}</span>
                <span class="stock-signal ${signalClass}">${stock.signal}</span>
            </div>
        `;
        container.appendChild(card);
    });

    // Render sparklines after cards are in DOM
    renderSparklines(stocks);
}

function renderSparklines(stocks) {
    stocks.forEach(stock => {
        const canvas = document.getElementById(`sparkline-${stock.ticker}`);
        if (!canvas || !stock.price_history || stock.price_history.length === 0) return;

        const ctx = canvas.getContext('2d');
        const prices = stock.price_history;
        const isUp = prices[prices.length - 1] >= prices[0];
        const color = isUp ? '#00DC82' : '#FF5252';

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: prices.map((_, i) => i),
                datasets: [{
                    data: prices,
                    borderColor: color,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    });
}

// --- GLOBAL INDICATORS SECTION ---
function renderGlobalIndicators(indicators) {
    const container = document.getElementById('global-container');
    if (!container || !indicators || indicators.length === 0) return;

    container.innerHTML = '';

    // Store indicators globally for modal access
    window.globalIndicators = indicators;

    indicators.forEach((indicator, index) => {
        const changeClass = indicator.change_pct >= 0 ? 'positive' : 'negative';
        const changeSign = indicator.change_pct >= 0 ? '+' : '';

        const card = document.createElement('div');
        card.className = 'global-card';
        card.style.cursor = 'pointer';
        card.onclick = () => openGlobalModal(index);
        card.innerHTML = `
            <div class="global-name">${indicator.name}</div>
            <div class="global-sparkline">
                <canvas id="global-spark-${indicator.ticker.replace(/[^a-zA-Z0-9]/g, '')}" width="100" height="25"></canvas>
            </div>
            <div class="global-price">${formatGlobalPrice(indicator)}</div>
            <div class="global-change ${changeClass}">
                ${changeSign}${indicator.change_pct.toFixed(2)}%
            </div>
        `;
        container.appendChild(card);
    });

    // Render sparklines after cards are in DOM
    renderGlobalSparklines(indicators);
}

function formatGlobalPrice(indicator) {
    // VIX doesn't need currency symbol
    if (indicator.ticker === '^VIX') {
        return indicator.price.toFixed(2);
    }
    // Commodities use $ 
    return `$${indicator.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function renderGlobalSparklines(indicators) {
    indicators.forEach(indicator => {
        const canvasId = `global-spark-${indicator.ticker.replace(/[^a-zA-Z0-9]/g, '')}`;
        const canvas = document.getElementById(canvasId);
        if (!canvas || !indicator.price_history || indicator.price_history.length === 0) return;

        const ctx = canvas.getContext('2d');
        const prices = indicator.price_history;
        const isUp = prices[prices.length - 1] >= prices[0];
        const color = isUp ? '#00DC82' : '#FF5252';

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: prices.map((_, i) => i),
                datasets: [{
                    data: prices,
                    borderColor: color,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    });
}

// Global chart modal instance
let globalModalChart = null;

function openGlobalModal(index) {
    const indicator = window.globalIndicators[index];
    if (!indicator || !indicator.price_history) return;

    const modal = document.getElementById('logic-modal');
    const body = document.getElementById('modal-body');
    const title = document.getElementById('modal-title');

    title.textContent = indicator.name;

    const changeClass = indicator.change_pct >= 0 ? 'positive' : 'negative';
    const changeSign = indicator.change_pct >= 0 ? '+' : '';
    const changeColor = indicator.change_pct >= 0 ? '#00DC82' : '#FF5252';

    body.innerHTML = `
        <div class="global-modal-header">
            <div class="global-modal-price">${formatGlobalPrice(indicator)}</div>
            <div class="global-modal-change ${changeClass}">
                ${changeSign}${indicator.change.toFixed(2)} (${changeSign}${indicator.change_pct.toFixed(2)}%)
            </div>
            <div class="global-modal-date">Última actualización: ${indicator.date}</div>
        </div>
        <div class="global-modal-chart-container">
            <canvas id="global-modal-chart"></canvas>
        </div>
        <div class="global-modal-info">
            <span>Tendencia de los últimos ${indicator.price_history.length} días</span>
        </div>
    `;

    modal.style.display = "flex";

    // Add close handlers
    document.querySelector('.close-modal').onclick = () => {
        modal.style.display = "none";
        if (globalModalChart) {
            globalModalChart.destroy();
            globalModalChart = null;
        }
    };
    window.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
            if (globalModalChart) {
                globalModalChart.destroy();
                globalModalChart = null;
            }
        }
    };

    // Render professional chart after DOM update
    setTimeout(() => {
        renderGlobalModalChart(indicator, changeColor);
    }, 100);
}

function renderGlobalModalChart(indicator, color) {
    const canvas = document.getElementById('global-modal-chart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const prices = indicator.price_history;

    // Destroy previous chart if exists
    if (globalModalChart) {
        globalModalChart.destroy();
    }

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 250);
    gradient.addColorStop(0, color + '40');
    gradient.addColorStop(1, color + '05');

    // Generate day labels
    const labels = prices.map((_, i) => {
        const daysAgo = prices.length - 1 - i;
        if (daysAgo === 0) return 'Hoy';
        if (daysAgo === 1) return 'Ayer';
        return `${daysAgo}d`;
    });

    globalModalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: prices,
                borderColor: color,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: color,
                fill: true,
                backgroundColor: gradient,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(20, 20, 20, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: color,
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: (items) => items[0].label,
                        label: (item) => {
                            const price = item.raw;
                            if (indicator.ticker === '^VIX') {
                                return `VIX: ${price.toFixed(2)}`;
                            }
                            return `Precio: $${price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: { display: false },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)',
                        maxTicksLimit: 6
                    }
                },
                y: {
                    display: true,
                    position: 'right',
                    grid: {
                        color: 'rgba(255,255,255,0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)',
                        callback: function (value) {
                            if (indicator.ticker === '^VIX') return value.toFixed(1);
                            return '$' + value.toLocaleString('en-US', { maximumFractionDigits: 0 });
                        }
                    }
                }
            }
        }
    });
}
