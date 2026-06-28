<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.1.0">
<NamedLayer><Name>ruang_terbuka_hijau</Name><UserStyle><Title>Ruang Terbuka Hijau — 2 Klas</Title><FeatureTypeStyle>
<Rule><Name>Non Hutan</Name><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>kelas_nume</ogc:PropertyName><ogc:Literal>1</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter><PolygonSymbolizer><Fill><CssParameter name="fill">#d7191c</CssParameter></Fill><Stroke><CssParameter name="stroke">#232323</CssParameter><CssParameter name="stroke-width">0.26</CssParameter></Stroke></PolygonSymbolizer></Rule>
<Rule><Name>Hutan</Name><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>kelas_nume</ogc:PropertyName><ogc:Literal>5</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter><PolygonSymbolizer><Fill><CssParameter name="fill">#2b83ba</CssParameter></Fill><Stroke><CssParameter name="stroke">#232323</CssParameter><CssParameter name="stroke-width">0.26</CssParameter></Stroke></PolygonSymbolizer></Rule>
</FeatureTypeStyle></UserStyle></NamedLayer></StyledLayerDescriptor>
