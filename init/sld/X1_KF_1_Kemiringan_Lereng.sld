<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:se="http://www.opengis.net/se" xmlns:ogc="http://www.opengis.net/ogc" version="1.1.0" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>kemiringan_lereng</Name>
    <UserStyle>
      <Title>Kemiringan Lereng — RdYlBu 5 Klas</Title>
      <Abstract>Categorized symbology: 5 kelas kemiringan lereng (kelas_nume 1-5), palet RdYlBu</Abstract>
      <FeatureTypeStyle>
        <Rule>
          <Name>0-2% (Datar)</Name>
          <Title>0-2% (Datar)</Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>kelas_nume</ogc:PropertyName>
              <ogc:Literal>1</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#d7191c</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">0.26</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>2-5% (Landai)</Name>
          <Title>2-5% (Landai)</Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>kelas_nume</ogc:PropertyName>
              <ogc:Literal>2</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#fdae61</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">0.26</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>5-15% (Bergelombang)</Name>
          <Title>5-15% (Bergelombang)</Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>kelas_nume</ogc:PropertyName>
              <ogc:Literal>3</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#ffffbf</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">0.26</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>15-40% (Curam)</Name>
          <Title>15-40% (Curam)</Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>kelas_nume</ogc:PropertyName>
              <ogc:Literal>4</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#abdda4</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">0.26</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>>40% (Sangat Curam)</Name>
          <Title>>40% (Sangat Curam)</Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>kelas_nume</ogc:PropertyName>
              <ogc:Literal>5</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#2b83ba</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#232323</CssParameter>
              <CssParameter name="stroke-width">0.26</CssParameter>
              <CssParameter name="stroke-linejoin">bevel</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
