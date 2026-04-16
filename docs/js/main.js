/*
*    main.js
*/


d3.json("data/buildings.json").then((data) => {
    
doubleBarChart("#chart1", data);
donutChart("#chart2", data);

}).catch((error) => {
    console.log(error);
});

/* 
TOTAL PRODUCTION VS CONSUMPTION
--> Gráfica de Barras dobles
*/

function doubleBarChart(container, data) {

    const containerWidth = document.querySelector(container).clientWidth;

	const width = containerWidth;
	const height = 400;

	const margin = {
		left: 80,
		right: 10,
		top: 10,
		bottom: 100
	};

	const innerWidth = width - margin.left - margin.right;
	const innerHeight = height - margin.top - margin.bottom;

    d3.select(container).html("");

	const svg = d3.select(container)
		.append("svg")
		.attr("width", width)
		.attr("height", height);

	const g = svg.append("g")
		.attr("transform", `translate(${margin.left}, ${margin.top})`);

	// Formato de datos
	data.forEach(d => {
		d.height = +d.height;
		d.weight = +d.weight;
	});

	// 🔹 Subgrupos (las dos barras)
	const subgroups = ["height", "weight"];

	// 🔹 Escala X principal
	const x = d3.scaleBand()
		.domain(data.map(d => d.name))
		.range([0, innerWidth])
		.padding(0.2);

	// 🔹 Escala X interna (para separar barras)
	const xSub = d3.scaleBand()
		.domain(subgroups)
		.range([0, x.bandwidth()])
		.padding(0.1);

	// 🔹 Escala Y
	const y = d3.scaleLinear()
		.domain([0, d3.max(data, d => Math.max(d.height, d.weight))])
		.range([innerHeight, 0]);

	// 🔹 Colores
	const color = d3.scaleOrdinal()
		.domain(subgroups)
		.range(["#5B8FF9", "#bbd3fc"]);

	// 🔹 Barras
	g.append("g")
		.selectAll("g")
		.data(data)
		.enter()
		.append("g")
		.attr("transform", d => `translate(${x(d.name)},0)`)
		.selectAll("rect")
		.data(d => subgroups.map(key => ({
			key: key,
			value: d[key]
		})))
		.enter()
		.append("rect")
		.attr("x", d => xSub(d.key))
		.attr("y", d => y(d.value))
		.attr("width", xSub.bandwidth())
		.attr("height", d => innerHeight - y(d.value))
		.attr("fill", d => color(d.key));

	// 🔹 Axis X
	g.append("g")
		.attr("transform", `translate(0, ${innerHeight})`)
		.call(d3.axisBottom(x))
		.selectAll("text")
		.attr("transform", "rotate(-40)")
		.style("text-anchor", "end");

	// 🔹 Axis Y
	g.append("g")
		.call(d3.axisLeft(y));

	// 🔹 Labels
	g.append("text")
		.attr("x", innerWidth / 2)
		.attr("y", innerHeight + 80)
		.attr("text-anchor", "middle")
		.text("Buildings");

	g.append("text")
		.attr("transform", "rotate(-90)")
		.attr("x", -innerHeight / 2)
		.attr("y", -60)
		.attr("text-anchor", "middle")
		.text("Height (m)");

	
}

/* 
--> Gráfica de Dona
*/

function donutChart(container, data) {

	const legendWidth = 200;

	const containerWidth = document.querySelector(container).clientWidth;

	const width = containerWidth;
	const height = 300;
	const radius = Math.min(width - legendWidth, height) / 2;

	// limpiar contenedor
	d3.select(container).html("");

	const svg = d3.select(container)
		.append("svg")
		.attr("class", "chart-svg")
		.attr("width", width)
		.attr("height", height);

	const g = svg.append("g")
		.attr("transform", `translate(${(width - legendWidth) / 2}, ${height / 2})`);

	// 🎨 colores suaves
	const color = d3.scaleOrdinal()
		.range(["#3B82F6", "#60A5FA", "#2563EB", "#1D4ED8", "#93C5FD", "#1E40AF"]);

	// arc
	const arc = d3.arc()
		.outerRadius(radius - 10)
		.innerRadius(radius - 60);

	// pie
	const pie = d3.pie()
		.padAngle(0.01)
		.value(d => d.count)
		.sort(null);

	// formatear datos
	data.forEach(d => {
		d.count = +d.count;
	});

	// ===== DONUT =====
	const arcs = g.selectAll("path")
		.data(pie(data))
		.enter()
		.append("path")
		.attr("fill", d => color(d.data.name))
		.attr("data-name", d => d.data.name) //Segun claude
		.attr("d", arc)
		.each(function(d) { this._current = d; });

	// animación
	arcs.transition()
		.duration(800)
		.attrTween("d", function(d) {
		const i = d3.interpolate({ startAngle: 0, endAngle: 0 }, d);
		return t => arc(i(t));
		});

	// hover (suave)
	arcs.on("mouseover", function() {
		d3.select(this).attr("opacity", 0.7);
	})
	.on("mouseout", function() {
		d3.select(this).attr("opacity", 1);
	});

	// ===== LEGEND =====
	const legend = svg.append("g")
		.attr("transform", `translate(${width - legendWidth + 10}, 30)`);

	const legendItem = legend.selectAll(".legend-item")
		.data(data)
		.enter()
		.append("g")
		.attr("class", "legend-item")
		.attr("transform", (d, i) => `translate(0, ${i * 22})`);

	// cuadritos de color
	legendItem.append("rect")
		.attr("width", 12)
		.attr("height", 12)
		.attr("rx", 3)
		.attr("fill", d => color(d.name));

	// texto
	legendItem.append("text")
		.attr("x", 18)
		.attr("y", 10)
		.style("font-size", "12px")
		.style("fill", "#555")
		.text(d => `${d.name}: ${d.count}`);

	// ===== INTERACCIÓN LEYENDA =====
// D3 v4/v5 → los parámetros son (d, i), sin event
legendItem
    .on("mouseover", function(d) {  // ← d es el dato directamente
        const hoveredName = d.name;

        arcs.attr("opacity", function() {
            const sliceName = d3.select(this).attr("data-name");
            return sliceName === hoveredName ? 1 : 0.2;
        });

        legendItem.select("text")
            .style("font-weight", "400")
            .style("fill", "#555");

        d3.select(this).select("text")
            .style("font-weight", "700")
            .style("fill", "#000");
    })
    .on("mouseout", function() {
        arcs.attr("opacity", 1);

        legendItem.select("text")
            .style("font-weight", "400")
            .style("fill", "#555");
    });
}
