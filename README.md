# MINT GeoViz
MINT-GeoViz is an interactive visualization library for large geospatial datasets that follow our proposed MINT NetCDF convention. Some examples of such datasets include a collection of year-long satellite images in Africa, global oceanographic time series and hydrographic measurements. Using efficient data access (via Dask), parallelized computation (via Numba, DataShader) and accurate visualization techniques (via DataShader, ColorCat), it works with datasets of millions or billions of data points in real-time. For example, a user can visualize the entire earthquake dataset (with 2.1 million seismological events) on a global map. Our tool goes a step further by allowing the user to perform new computations as they explore the visualization, eg. computing aggregated statistics, transforming high dimensional data to a time series.

This repo contains tools for a proof of concept visualization of geospatial datasets that follow MINT NetCDF convention as described in <a href="https://github.com/mintproject/MINT-NetCDF-Convention">this proposal</a>. 

![demo1-1](assets/fldas-demo-part1-1.gif)
![demo1-2](assets/fldas-demo-part1-2.gif)
![demo1-3](assets/fldas-demo-part1-3.gif)
![demo1-4](assets/fldas-demo-part1-4.gif)
![demo-latlon](assets/fldas_latlon_cross.gif)

For full demo videos, please visit <a href="https://drive.google.com/open?id=1t9E5HsUOre0CgAevkdRAxgaRQghJ_i2v"> here </a>.
