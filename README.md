[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<div align="center">
    <a href="https://github.com/B-Pump">
        <img src="https://black_hole-3kf-1-q4182424.deta.app/api/photo/j96zwgywbt3r.png" alt="Logo" width="120" height="120">
    </a>
    <h3 align="center">B-Pump API</h3>
    <p align="center">Backend API for the B-Pump project</p>
</div>

<details>
    <summary>Table of Contents</summary>
    <ol>
        <li>
            <a href="#about-the-project">About The Project</a>
            <ul>
                <li><a href="#built-with">Built With</a></li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#prerequisites">Prerequisites</a></li>
                <li><a href="#installation">Installation</a></li>
            </ul>
        </li>
        <li><a href="#usage">Usage</a></li>
        <li><a href="#license">License</a></li>
        <li><a href="#contact">Contact</a></li>
    </ol>
</details>

## About The Project

![Screenshot][repo-screenshot]

### Built With

-   [FastAPI](https://fastapi.tiangolo.com/)

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

1. Create an empty [PostgreSQL](https://www.postgresql.org/download/) database.

### Installation

1. Clone the repo
    ```sh
    git clone https://github.com/B-Pump/bpump-api.git
    ```
2. Install PIP packages
    ```sh
    pip install -r requirements.txt
    ```
3. Create a `.env` file
    ```sh
    touch .env
    ```
4. Copy content of `.env.example` file and paste into your new `.env` file
5. Paste after _DB_URL_ your database URL

## Usage

-   Launch the server
    ```sh
    uvicorn main:app --reload
    ```

## Contributing

Contributions are not welcome as this is a project developed for school Olympiads. However, you can still report bugs if you find any by opening an issue. This would be greatly appreciated !

## License

Distributed under the MIT License. See [`LICENSE`][license-url] for more information.

## Contact

B-Pump: [b.pump.project@gmail.com](mailto:b.pump.project@gmail.com)

Org Link: [https://github.com/B-Pump](https://github.com/B-Pump)

[stars-shield]: https://img.shields.io/github/stars/B-Pump/bpump-api.svg?style=for-the-badge
[stars-url]: https://github.com/B-Pump/bpump-api/stargazers
[issues-shield]: https://img.shields.io/github/issues/B-Pump/bpump-api.svg?style=for-the-badge
[issues-url]: https://github.com/B-Pump/bpump-api/issues
[license-shield]: https://img.shields.io/github/license/B-Pump/bpump-api.svg?style=for-the-badge
[license-url]: https://github.com/B-Pump/bpump-api/blob/master/LICENSE
[repo-screenshot]: https://i.ibb.co/Y2n59kG/sss.png
