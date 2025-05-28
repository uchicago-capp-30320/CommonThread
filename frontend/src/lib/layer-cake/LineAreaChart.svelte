<script>
	import { LayerCake, Svg } from 'layercake';
	import { timeFormat } from 'd3-time-format';

	import Line from './Line.svelte';
	import Area from './Area.svelte';
	import AxisX from './AxisX.svelte';
	import AxisY from './AxisY.svelte';

	let { xKey, yKey, data, stroke, fill } = $props();
	const formatLabelX = timeFormat('%b %d');
</script>

<div class="chart-container">
	<LayerCake
		padding={{ top: 8, right: 10, bottom: 20, left: 25 }}
		x={xKey}
		y={yKey}
		yDomain={[0, null]}
		{data}
	>
		<Svg>
			<AxisX format={formatLabelX} />
			<AxisY ticks={4} />
			<Line {stroke} />
			<Area {fill} />
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
