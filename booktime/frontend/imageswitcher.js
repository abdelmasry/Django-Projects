const React = require("react");
const ReactDOM = require("react-dom");

const e = React.createElement;

class ImageBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      currentImage: this.props.imageStart,
    };
  }

  click(image) {
    this.setState({
      currentImage: image,
    });
  }

  render() {
    const images = this.props.images.map((i) =>
      e(
        "div",
        { className: "image", key: i.id },
        e("img", {
          onClick: this.click.bind(this, i),
          src: i.thumbnail,
          style: { width: "30px", height: "50px" }, // Apply inline styles for thumbnail image
        })
      )
    );

    return e(
      "div",
      { className: "container-fluid" }, // Add a container class for styling
      e(
        "div",
        { className: "current-image", style: { marginBottom: "20px" } }, // Apply margin bottom to create space
        e("img", {
          style: { width: "300px", height: "450px", border: "2px solid black",
          borderRadius: "5px" },
          src: this.state.currentImage.image,
          // Apply inline styles for current image
        })
      ),
      e(
        "div",
        {
          className: "gallery",
          style: {
            display: "flex",
          },
        },
        images.map((image, index) => {
          // Apply margin-right to all images except the last one
          const imageStyle = {
                  marginRight: "10px",
                  border: "2px solid black",
                  borderRadius: "5px",
                }
              ;
          return e("div", { key: index, style: imageStyle }, image);
        })
      )
    );
  }
}

window.React = React;
window.ReactDOM = ReactDOM;
window.ImageBox = ImageBox;
module.exports = ImageBox;
