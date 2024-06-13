<a name="readme-top"></a>

<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://gitlab.tue.nl/20233498/dbl_data_challenge">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">DBL Data Challenge</h3>

  <p align="center">
    Weird data challenge
    <br />
    <a href="https://gitlab.tue.nl/20233498/dbl_data_challenge/-/blob/main/README.md?ref_type=heads"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://gitlab.tue.nl/20233498/dbl_data_challenge">View Demo</a>
    ·
    <a href="https://gitlab.tue.nl/20233498/dbl_data_challenge/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://gitlab.tue.nl/20233498/dbl_data_challenge/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
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
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com/)

This is a weird data challenge project, mainly about data preprocessing and data analysis (so data science stuff). Also use a sentiment analysis model.

<!-- Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description` -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

<!-- * [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url] -->

* [![python][Python]][Python]
* [![mysql][MySQL]][MySQL]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

Clone the project and download the data. Unzip and put the json files inside `data/` folder. Note that there might still exists a zip file inside `data/` after extracting.

To remove the zip file, you can do:
```sh
rm -f data/data.zip
```

## Prerequisites

* Install [mysql](https://www.mysql.com/downloads/)
* Install [python3](https://www.python.org/downloads/)

<!-- * python
  ```sh
  pip install -r requirements.txt
  ``` -->

## Installation

1. Clone the repo
   ```sh
   git clone ...
   ```
2. Install python packages
   ```sh
   pip install -r requirements.txt
   ```
3. Create your .env file
   ```sh
   touch .env
   ```
4. Setup your .env file, it should follow this format
   ```sh
   HOST=your_host
   USERNAME=your_username
   PASSWORD=your_pass
   DATABASE=your_dbname
   ```
5. Go to mysql shell and create your database
   ```mysql
   create database your_dbname;
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

1. Load the tweets into csv file
    ```sh
    python preprocess/ultimate_tweet_loader.py
    ```
2. Type `all`.
3. Change the name of the resulting csv file `tweets_dataset_all.csv` to `combined_dataset.csv`
    ```sh
    mv tweets_dataset_all.csv combined_dataset.csv
    ```
4. Run `main.py`
    ```sh
    python main.py
    ```
5. Type `csvadduser` to load the users information to a csv file.
6. Type `setup` to load the data from csv file to your mysql tables and extract conversations from the tweets data.
7. Type `categorize` to add the categorize the data into topics.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Utilize GPU to parallel processing in performing sentiment analysis in batch
- [ ] Use multithreading to perform I/O tasks when loading tweets data to a csv file
- [ ] Add time remaining when loading the data
    - [ ] Add log file to report errors when loading the data
    - [ ] Add checkpoints

See the [open issues](https://gitlab.tue.nl/20233498/dbl_data_challenge/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the TU/e License. Have to pay 69 euros to clone the repo.

<!-- Distributed under the MIT License. See `LICENSE.txt` for more information. -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

<!-- Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com -->

Go to momentum at 9am in the morning, knock on the side door 69 times, I will appear, else find my name being hidden in this repository and reverse search my contact.

Project Link: [https://gitlab.tue.nl/20233498/dbl_data_challenge](https://gitlab.tue.nl/20233498/dbl_data_challenge)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Never]()
* [Gonna]()
* [Give]()
* [You]()
* [Up]()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://gitlab.tue.nl/20233498/dbl_data_challenge/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://gitlab.tue.nl/20233498/dbl_data_challenge/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://gitlab.tue.nl/20233498/dbl_data_challenge/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://gitlab.tue.nl/20233498/dbl_data_challenge/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://gitlab.tue.nl/20233498/dbl_data_challenge/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[MySQL]: https://img.shields.io/badge/-MySQL-4479A1?style=flat-square&logo=mysql&labelColor=4479A1&logoColor=FFF
[MySQL-url]: https://www.mysql.com/