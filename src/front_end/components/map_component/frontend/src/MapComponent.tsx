import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import DeckGL from "@deck.gl/react"
import { setDefaultCredentials, BASEMAP } from "@deck.gl/carto"
import { StaticMap } from "react-map-gl"
import { JSONConverter } from "@deck.gl/json"
import { PickInfo } from "@deck.gl/core/lib/deck"

const configuration = {
  layers: require("@deck.gl/layers"),
}

setDefaultCredentials({
  username: "public",
  apiKey: "default_public",
})

interface State {
  selectedHexId: string
}

class MapComponent extends StreamlitComponentBase<State> {
  public state = { selectedHexId: ""}


  public render = (): ReactNode => {
    const initialViewState = this.props.args["initialViewState"]

    const jsonConverter = new JSONConverter({ configuration })
    const layers = this.props.args["layers"].map((x: object) =>
      jsonConverter.convert(x)
    )

    const { theme } = this.props
    const style: React.CSSProperties = {}
    if (theme) {
    }

    const mapOnClick = (info: PickInfo<any>, e: MouseEvent) => {
      const hex_id = info.object?.hex_id ?? this.state.selectedHexId
      console.log(hex_id)
      this.setState({selectedHexId: hex_id})
      Streamlit.setComponentValue(hex_id)
    }

    return (
      <span>
        <div style={{ position: "relative", height: "500px" }}>
          <DeckGL
            initialViewState={initialViewState}
            controller={true}
            layers={layers}
            height={"500px"}
            onClick={mapOnClick}
            getTooltip={(object: PickInfo<any>) =>
              object && {
                text: `Hex ID: ${
                  object.object?.hex_id ?? ""
                }\nAverage price: ${
                  object.object?.price ?? 0
                }\nAverage price per m2: ${
                  object.object?.price_per_m ?? 0
                }\nAverage area: ${
                  object.object?.area ?? 0
                }\nNumber of offers: ${object.object?.count ?? 0}`,
              }
            }
          >
            <StaticMap mapStyle={BASEMAP.POSITRON} />
          </DeckGL>
        </div>
      </span>
    )
  }
}

export default withStreamlitConnection(MapComponent)
