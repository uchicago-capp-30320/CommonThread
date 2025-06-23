<script>
	import { LayerCake, Svg } from 'layercake';
	import { scaleBand } from 'd3-scale';

	import Bar from './Bar.svelte';
	import AxisX from './AxisX.svelte';
	import AxisY from './AxisY.svelte';

	let { xKey, yKey, data } = $props();

	// // This example loads csv data as json using @rollup/plugin-dsv
	// import data from './_data/groups.csv';
</script>

<div class="chart-container">
	<LayerCake
		padding={{ bottom: 20, left: 100 }}
		x={xKey}
		y={yKey}
		yScale={scaleBand().paddingInner(0.05)}
		xDomain={[0, null]}
		{data}
	>
		<Svg>
			<AxisX tickMarks baseline snapLabels />
			<AxisY tickMarks gridlines={false} />
			<Bar fill="#133335" />
		</Svg>
	</LayerCake>
</div>

<style>
	/*
      The wrapper div needs to have an explicit width and height in CSS.
      It can also be a flexbox child or CSS grid element.
      The point being it needs dimensions since the <LayerCake> element will
      expand to fill it.
    */
	.chart-container {
		width: 100%;
		height: 250px;
	}
</style>
