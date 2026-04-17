// 1. Create a Global and invisible Tooltip that we will share among all charts
const tooltip = d3.select("body").append("div")
    .attr("class", "d3-tooltip")
    .style("position", "absolute")
    .style("background", "rgba(255, 255, 255, 0.95)")
    .style("border", "1px solid #ccc")
    .style("border-radius", "8px")
    .style("padding", "12px")
    .style("font-size", "13px")
    .style("color", "#333")
    .style("box-shadow", "0 4px 15px rgba(0,0,0,0.15)")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("z-index", "9999");

// 2. Load the Data
d3.json("data/dashboard_data.json").then((data) => {

    // --- KPIs ---
    if (d3.select("#kpi-savings").node()) {
        d3.select("#kpi-savings").text(`$${data.summary.estimated_savings_dollars.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`);
        d3.select("#kpi-solar").text(`${Math.round(data.summary.total_solar).toLocaleString()} kWh`);
        d3.select("#kpi-peak").text(`${data.summary.peak_load_hour}:00`);
    }

    // --- CHART RENDERING ---
    // Req: Production vs consumption per household type
    renderDoubleBar("#chart1", data.by_house_type, "house_type", "House Type");

    // Req: Production vs consumption per wealth level
    renderDoubleBar("#chart2", data.by_wealth, "wealth_level", "Wealth Level");

    // Req: Total production vs consumption / Energy export to the grid
    renderDonut("#chart3", data.summary);

    // Req: Duck Curve / Peak production vs peak consumption times / Energy surplus vs deficit
    renderDuckCurve("#chart4", data.duck_curve, data.summary);

    // Req: Battery storage utilization
    renderBatteryArea("#chart5", data.duck_curve);

    // Req: Cost savings from self-consumption / Exported energy (Leaf Project Bubble Chart)
    renderBubbleChart("#chart6", data.by_house);

    // Req: Adoption rates (Energy Independence) by Wealth Level
    renderStackedChart("#chart7", data.by_wealth);

}).catch((error) => {
    console.error("Error loading JSON. Make sure the local server is running.", error);
});


/* =======================================================================
 * FUNCTION 1: DOUBLE BAR CHART (PRODUCTION VS CONSUMPTION)
 * ======================================================================= */
function renderDoubleBar(container, data, keyName, xAxisLabel) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 500;
    const height = 350;
    const margin = { left: 60, right: 20, top: 20, bottom: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");
    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);

    const subgroups = ["load_kw", "solar_gen_kw"];
    const labels = { "load_kw": "Consumption", "solar_gen_kw": "Solar Production" };

    const x = d3.scaleBand().domain(data.map(d => d[keyName].replace("_", " "))).range([0, innerWidth]).padding(0.2);
    const xSub = d3.scaleBand().domain(subgroups).range([0, x.bandwidth()]).padding(0.05);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => Math.max(d.load_kw, d.solar_gen_kw)) * 1.1]).range([innerHeight, 0]);
    const color = d3.scaleOrdinal().domain(subgroups).range(["#EF4444", "#10B981"]);

    // Bars
    const bars = g.append("g").selectAll("g").data(data).enter().append("g")
        .attr("transform", d => `translate(${x(d[keyName].replace("_", " "))},0)`)
        .selectAll("rect").data(d => subgroups.map(key => ({ key: key, value: d[key], parent: d[keyName] })))
        .enter().append("rect")
        .attr("x", d => xSub(d.key)).attr("y", d => y(d.value))
        .attr("width", xSub.bandwidth()).attr("height", d => innerHeight - y(d.value))
        .attr("fill", d => color(d.key)).attr("rx", 3);

    // Interactivity
    bars.on("mouseover", function (d) {
        d3.select(this).attr("opacity", 0.8);
        tooltip.style("opacity", 1).html(`
            <strong>${d.parent.replace("_", " ")}</strong><br/>
            ${labels[d.key]}: <strong>${Math.round(d.value).toLocaleString()} kWh</strong>
        `);
    }).on("mousemove", function () {
        tooltip.style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px");
    }).on("mouseout", function () {
        d3.select(this).attr("opacity", 1);
        tooltip.style("opacity", 0);
    });

    g.append("g").attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(x));
    g.append("g").call(d3.axisLeft(y).ticks(6).tickFormat(d => `${d / 1000}k`));
    g.append("text").attr("transform", "rotate(-90)").attr("x", -innerHeight / 2).attr("y", -40).attr("text-anchor", "middle").style("font-size", "12px").text("Energy (kWh)");
}

/* =======================================================================
 * FUNCTION 2: DONUT CHART (DESTINATION OF PRODUCED ENERGY)
 * ======================================================================= */
function renderDonut(container, summaryData) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 500;
    const height = 350;
    const legendWidth = 200;
    const radius = Math.min(width - legendWidth, height) / 2;

    d3.select(container).html("");
    const data = [
        { name: "Self-Consumed (Saved $)", count: summaryData.total_self_consumption },
        { name: "Exported to Grid", count: summaryData.total_export }
    ];

    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${(width - legendWidth) / 2}, ${height / 2})`);
    const color = d3.scaleOrdinal().domain(data.map(d => d.name)).range(["#10B981", "#3B82F6"]);

    const arc = d3.arc().outerRadius(radius - 10).innerRadius(radius - 60);
    const pie = d3.pie().padAngle(0.02).value(d => d.count).sort(null);

    const arcs = g.selectAll("path").data(pie(data)).enter().append("path")
        .attr("fill", d => color(d.data.name)).attr("d", arc)
        .on("mouseover", function (d) {
            d3.select(this).attr("opacity", 0.7);
            const percent = ((d.data.count / summaryData.total_solar) * 100).toFixed(1);
            tooltip.style("opacity", 1).html(`<strong>${d.data.name}</strong><br/>${Math.round(d.data.count).toLocaleString()} kWh (${percent}%)`);
        })
        .on("mousemove", () => tooltip.style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px"))
        .on("mouseout", function () { d3.select(this).attr("opacity", 1); tooltip.style("opacity", 0); });

    // Legend
    const legend = svg.append("g").attr("transform", `translate(${width - legendWidth + 20}, ${height / 2 - 30})`);
    const legendItem = legend.selectAll(".legend-item").data(data).enter().append("g").attr("transform", (d, i) => `translate(0, ${i * 30})`);
    legendItem.append("rect").attr("width", 14).attr("height", 14).attr("rx", 3).attr("fill", d => color(d.name));
    legendItem.append("text").attr("x", 22).attr("y", 12).style("font-size", "13px").text(d => d.name);
}

/* =======================================================================
 * FUNCTION 3: THE DUCK CURVE (SURPLUS/DEFICIT & PEAKS)
 * ======================================================================= */
function renderDuckCurve(container, data, summary) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 600;
    const height = 400;
    const margin = { left: 50, right: 30, top: 20, bottom: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");
    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);

    const x = d3.scaleLinear().domain([0, 23]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([d3.min(data, d => d.net_load_kw) - 1, d3.max(data, d => d.load_kw) + 1]).range([innerHeight, 0]);

    // Zero Line (Grid Neutrality)
    g.append("line").attr("x1", 0).attr("x2", innerWidth).attr("y1", y(0)).attr("y2", y(0))
        .attr("stroke", "#999").attr("stroke-dasharray", "4,4");

    // Deficit / Surplus Area
    const area = d3.area().x(d => x(d.hour)).y0(y(0)).y1(d => y(d.net_load_kw)).curve(d3.curveMonotoneX);
    g.append("path").datum(data).attr("fill", "#10B981").attr("opacity", 0.15).attr("d", area);

    // Main lines
    const loadLine = d3.line().x(d => x(d.hour)).y(d => y(d.load_kw)).curve(d3.curveMonotoneX);
    const solarLine = d3.line().x(d => x(d.hour)).y(d => y(d.solar_gen_kw)).curve(d3.curveMonotoneX);
    const netLine = d3.line().x(d => x(d.hour)).y(d => y(d.net_load_kw)).curve(d3.curveMonotoneX);

    g.append("path").datum(data).attr("fill", "none").attr("stroke", "#EF4444").attr("stroke-width", 2).attr("d", loadLine);
    g.append("path").datum(data).attr("fill", "none").attr("stroke", "#F59E0B").attr("stroke-width", 2).attr("d", solarLine);
    g.append("path").datum(data).attr("fill", "none").attr("stroke", "#2563EB").attr("stroke-width", 3).attr("d", netLine);

    // Peak Markers
    const peakLoadData = data.find(d => d.hour === summary.peak_load_hour);
    const peakSolarData = data.find(d => d.hour === summary.peak_solar_hour);

    if (peakLoadData) {
        g.append("circle").attr("cx", x(peakLoadData.hour)).attr("cy", y(peakLoadData.load_kw)).attr("r", 6).attr("fill", "#EF4444");
        g.append("text").attr("x", x(peakLoadData.hour)).attr("y", y(peakLoadData.load_kw) - 10).attr("text-anchor", "middle").style("font-size", "11px").style("font-weight", "bold").text("Peak Demand");
    }
    if (peakSolarData) {
        g.append("circle").attr("cx", x(peakSolarData.hour)).attr("cy", y(peakSolarData.solar_gen_kw)).attr("r", 6).attr("fill", "#F59E0B");
        g.append("text").attr("x", x(peakSolarData.hour)).attr("y", y(peakSolarData.solar_gen_kw) - 10).attr("text-anchor", "middle").style("font-size", "11px").style("font-weight", "bold").text("Peak Solar");
    }

    // Invisible Tooltip Tracker
    const tracker = g.append("rect").attr("width", innerWidth).attr("height", innerHeight).attr("fill", "transparent");
    const verticalLine = g.append("line").attr("y1", 0).attr("y2", innerHeight).attr("stroke", "#333").attr("stroke-dasharray", "3,3").style("opacity", 0);

    tracker.on("mousemove", function () {
        const mx = d3.mouse(this)[0];
        const hour = Math.round(x.invert(mx));
        if (hour >= 0 && hour <= 23) {
            verticalLine.attr("x1", x(hour)).attr("x2", x(hour)).style("opacity", 1);
            const d = data.find(item => item.hour === hour);
            tooltip.style("opacity", 1).html(`
                <strong>Hour: ${hour}:00</strong><br/>
                <span style="color:#EF4444">Demand: ${d.load_kw.toFixed(2)} kW</span><br/>
                <span style="color:#F59E0B">Solar: ${d.solar_gen_kw.toFixed(2)} kW</span><br/>
                <span style="color:#2563EB"><b>Net Load: ${d.net_load_kw.toFixed(2)} kW</b></span>
            `).style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px");
        }
    }).on("mouseout", function () { verticalLine.style("opacity", 0); tooltip.style("opacity", 0); });

    g.append("g").attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(x).ticks(12).tickFormat(d => d + ":00"));
    g.append("g").call(d3.axisLeft(y));
}

/* =======================================================================
 * FUNCTION 4: BATTERY UTILIZATION (AREA CHART)
 * ======================================================================= */
function renderBatteryArea(container, data) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 500;
    const height = 350;
    const margin = { left: 50, right: 20, top: 20, bottom: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");
    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);

    const x = d3.scaleLinear().domain([0, 23]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.battery_soc_kwh) * 1.2]).range([innerHeight, 0]);

    const area = d3.area().x(d => x(d.hour)).y0(innerHeight).y1(d => y(d.battery_soc_kwh)).curve(d3.curveMonotoneX);
    const line = d3.line().x(d => x(d.hour)).y(d => y(d.battery_soc_kwh)).curve(d3.curveMonotoneX);

    g.append("path").datum(data).attr("fill", "#10B981").attr("opacity", 0.4).attr("d", area);
    g.append("path").datum(data).attr("fill", "none").attr("stroke", "#059669").attr("stroke-width", 3).attr("d", line);

    // Interactive points
    g.selectAll("circle").data(data).enter().append("circle")
        .attr("cx", d => x(d.hour)).attr("cy", d => y(d.battery_soc_kwh)).attr("r", 4).attr("fill", "#fff").attr("stroke", "#059669").attr("stroke-width", 2)
        .on("mouseover", function (d) {
            d3.select(this).attr("r", 7);
            tooltip.style("opacity", 1).html(`<strong>Hour: ${d.hour}:00</strong><br/>Avg Battery: ${d.battery_soc_kwh.toFixed(2)} kWh`);
        })
        .on("mousemove", () => tooltip.style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px"))
        .on("mouseout", function () { d3.select(this).attr("r", 4); tooltip.style("opacity", 0); });

    g.append("g").attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(x).ticks(12).tickFormat(d => d + ":00"));
    g.append("g").call(d3.axisLeft(y));
}

/* =======================================================================
 * FUNCTION 5: BUBBLE CHART (COST SAVINGS VS EXPORT PER HOUSE)
 * ======================================================================= */
function renderBubbleChart(container, data) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 600;
    const height = 400;
    const margin = { left: 60, right: 30, top: 20, bottom: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");
    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);

    const x = d3.scaleLinear().domain([0, d3.max(data, d => d.grid_export_kw) * 1.1]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.savings_dollars) * 1.1]).range([innerHeight, 0]);
    const r = d3.scaleSqrt().domain([0, d3.max(data, d => d.self_consumption_kw)]).range([4, 25]);
    const color = d3.scaleOrdinal().domain(["Low_Income", "Middle_Income", "Luxury"]).range(["#3B82F6", "#F59E0B", "#8B5CF6"]);

    // Axes
    g.append("g").attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(x));
    g.append("g").call(d3.axisLeft(y).tickFormat(d => `$${d}`));
    g.append("text").attr("x", innerWidth / 2).attr("y", innerHeight + 40).attr("text-anchor", "middle").style("font-size", "12px").text("Energy Exported to Grid (kWh)");
    g.append("text").attr("transform", "rotate(-90)").attr("x", -innerHeight / 2).attr("y", -45).attr("text-anchor", "middle").style("font-size", "12px").text("Estimated Savings ($)");

    // Bubbles
    g.selectAll("circle").data(data).enter().append("circle")
        .attr("cx", d => x(d.grid_export_kw))
        .attr("cy", d => y(d.savings_dollars))
        .attr("r", d => r(d.self_consumption_kw))
        .attr("fill", d => color(d.wealth_level))
        .attr("opacity", 0.7).attr("stroke", "#fff").attr("stroke-width", 1)
        .on("mouseover", function (d) {
            d3.select(this).attr("opacity", 1).attr("stroke", "#333").attr("stroke-width", 2);
            tooltip.style("opacity", 1).html(`
                <strong>${d.house_id} (${d.house_type.replace("_", " ")})</strong><br/>
                Wealth: ${d.wealth_level.replace("_", " ")}<br/>
                <hr style="margin:5px 0;">
                Savings: $${d.savings_dollars.toFixed(2)}<br/>
                Exported: ${d.grid_export_kw.toFixed(1)} kWh<br/>
                Self-Consumed: ${d.self_consumption_kw.toFixed(1)} kWh
            `);
        })
        .on("mousemove", () => tooltip.style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px"))
        .on("mouseout", function () { d3.select(this).attr("opacity", 0.7).attr("stroke", "#fff").attr("stroke-width", 1); tooltip.style("opacity", 0); });
}

/* =======================================================================
 * FUNCTION 6: STACKED CHART (ADOPTION / ENERGY INDEPENDENCE)
 * ======================================================================= */
function renderStackedChart(container, data) {
    if (!document.querySelector(container)) return;
    const width = document.querySelector(container).clientWidth || 500;
    const height = 350;
    const margin = { left: 60, right: 150, top: 20, bottom: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");
    const formattedData = data.map(d => ({
        group: d.wealth_level.replace("_", " "),
        "Self-Consumed Solar": d.self_consumption_kw,
        "Imported from Grid": Math.max(0, d.load_kw - d.self_consumption_kw)
    }));

    const subgroups = ["Self-Consumed Solar", "Imported from Grid"];
    const groups = formattedData.map(d => d.group);
    const stack = d3.stack().keys(subgroups);
    const stackedData = stack(formattedData);

    const svg = d3.select(container).append("svg").attr("width", width).attr("height", height);
    const g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);

    const x = d3.scaleBand().domain(groups).range([0, innerWidth]).padding(0.3);
    const y = d3.scaleLinear().domain([0, d3.max(stackedData[stackedData.length - 1], d => d[1]) * 1.1]).range([innerHeight, 0]);
    const color = d3.scaleOrdinal().domain(subgroups).range(["#10B981", "#EF4444"]);

    const layers = g.selectAll(".layer").data(stackedData).enter().append("g").attr("fill", d => color(d.key));

    layers.selectAll("rect").data(d => d).enter().append("rect")
        .attr("x", d => x(d.data.group)).attr("y", d => y(d[1]))
        .attr("height", d => y(d[0]) - y(d[1])).attr("width", x.bandwidth())
        .on("mouseover", function (d) {
            const subgroupName = d3.select(this.parentNode).datum().key;
            const value = d[1] - d[0];
            d3.select(this).attr("opacity", 0.7);
            tooltip.style("opacity", 1).html(`<strong>${d.data.group}</strong><br/>${subgroupName}: ${Math.round(value).toLocaleString()} kWh`);
        })
        .on("mousemove", () => tooltip.style("left", (d3.event.pageX + 15) + "px").style("top", (d3.event.pageY - 40) + "px"))
        .on("mouseout", function () { d3.select(this).attr("opacity", 1); tooltip.style("opacity", 0); });

    g.append("g").attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(x));
    g.append("g").call(d3.axisLeft(y).ticks(6).tickFormat(d => `${d / 1000}k`));

    const legend = svg.append("g").attr("transform", `translate(${innerWidth + margin.left + 20}, ${margin.top})`);
    const legendItem = legend.selectAll(".legend-item").data(subgroups.slice().reverse()).enter().append("g").attr("transform", (d, i) => `translate(0, ${i * 25})`);
    legendItem.append("rect").attr("width", 14).attr("height", 14).attr("rx", 3).attr("fill", d => color(d));
    legendItem.append("text").attr("x", 20).attr("y", 12).style("font-size", "12px").text(d => d);
}
