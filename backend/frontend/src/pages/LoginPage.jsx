import React, { Component } from "react";
import { getAllSatellites } from "../api/satelliteService";

export default class LoginPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      satellites: [],
      error: null,
    };
  }

  componentDidMount() {
    getAllSatellites()
      .then((data) => this.setState({ satellites: data }))
      .catch((err) => this.setState({ error: err.message }));
  }

  render() {
    const { satellites, error } = this.state;

    if (error) return <p>Error: {error}</p>;

    return (
      <div>
        <h1>Login Page</h1>
        <ul>
          {satellites.map((sat) => (
            <li key={sat.satellite_id}>
              {sat.name} — {sat.orbit_type}
            </li>
          ))}
        </ul>
      </div>
    );
  }
}
