<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.1.0">
  <NamedLayer>
    <Name>kenaikan_muka_laut</Name>
    <UserStyle>
      <Title>Kenaikan Muka Laut — 3 Klas</Title>
      <FeatureTypeStyle>
        <Rule><Name>Data Tidak Tersedia</Name><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>kelas_nume</ogc:PropertyName><ogc:Literal>1</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter><PolygonSymbolizer><Fill><CssParameter name="fill">#d7191c</CssParameter></Fill><Stroke><CssParameter name="stroke">#232323</CssParameter><CssParameter name="stroke-width">0.26</CssParameter><CssParameter name="stroke-linejoin">bevel</CssParameter></Stroke></PolygonSymbolizer></Rule>
        <Rule><Name>Potensi / Sedang</Name><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>kelas_nume</ogc:PropertyName><ogc:Literal>3</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter><PolygonSymbolizer><Fill><CssParameter name="fill">#ffffbf</CssParameter></Fill><Stroke><CssParameter name="stroke">#232323</CssParameter><CssParameter name="stroke-width">0.26</CssParameter><CssParameter name="stroke-linejoin">bevel</CssParameter></Stroke></PolygonSymbolizer></Rule>
        <Rule><Name>Tinggi</Name><ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>kelas_nume</ogc:PropertyName><ogc:Literal>5</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter><PolygonSymbolizer><Fill><CssParameter name="fill">#2b83ba</CssParameter></Fill><Stroke><CssParameter name="stroke">#232323</CssParameter><CssParameter name="stroke-width">0.26</CssParameter><CssParameter name="stroke-linejoin">bevel</CssParameter></Stroke></PolygonSymbolizer></Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
