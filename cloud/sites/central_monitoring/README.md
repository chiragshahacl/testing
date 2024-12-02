# Tucana Central Monitoring Station

## Overview

The Central Monitoring Station (CMS) web application plays a pivotal role as a primary interface between users and the entire system. It facilitates concurrent monitoring of vital signs and patient information for multiple beds. Additionally, it allows the association between beds and patient monitors while enabling the triggering of alerts for any vital or device-related issues that may arise from Patient Monitors and various Sensors.

Notably, CMS operates independently without direct communication with databases, devices, or platforms. Instead, it interfaces with server-side gateways for all information storage and retrieval, encompassing both static and real-time data. To ensure the security of transmitted information, the application exclusively utilizes secure communication channels. Moreover, user authentication is a requisite for accessing the application, and the authentication service establishes an expiration time, enhancing overall security measures. This design ensures a secure, efficient, and user-friendly experience for monitoring vital signs and patient information through the CMS web application.

The CMS Web application will be used from a Central Monitoring Desktop application created on Electron, utilizing Kiosk mode. To facilitate this CMS should keep track of what beds and alerts are currently being shown. This includes showing if every bed is shown in at least one screen, and managing audio alerts so no two alerts are playing at the same time and the sound is for the highest priority one.

## Flows

### AUTHENTICATION

+_First time authentication flow_ goes through the Login page. It communicates with the Web Gateway to authenticate a user and only allows user to proceed to the home page if authentication is successfull.

+_Logout de-authentication flow_ goes through the LogoutModal component, potentially accessible on any authenticated page. It removes all user tokens related to the session and redirects the user back to the login page

+_Automatic authentication flow_ is present in both Root page and Login page. It detects if the user has an access token and refresh token and if so redirects the user to home screen

+_Automatic de-authentication flow_ is present in the AuthenticatedRoot Layout. It detects if the user doesn't have an access token or refresh token and redirects them to login if so. This flow is also present in the httpClient utils Interceptor. It redirects to login if any requests are met with unauthorized response

### VITALS DISPLAY

+_Vitals display flow_ is present on both Home and Details pages. It uses the information received from the Realtime Gateway to display appropriate vitals information for all patients in the beds currently part of the selected group. Which vitals are displayed for which patients depends on the current page and the selected patient

+_Graphs display flow_ is very similar to the _Vitals display flow_. Some finer points of the implementation can be found on the GraphCard component. CMS is currently using SciChart as its Graph Display solution

### ALERTS

+_Vitals and Technical Alerts display flow_ is present on both Home and Details pages. It uses the information received on the web group alerts endpoint from Web Gateway (vitals), the information received on the device endpoint from Web Gateway (technical), the alerts received from Realtime Gateway (both vitals and technical), and locally raised alerts (unresponsive or not shown Patient Monitors)

+_Alert Sound flow_ is mainly managed on the AudioManagerContext Context. It manages when alerts should play, which audio file to play and how frequently, and communication between different CMS screens so no two alert sounds are playing at the same time

### MANAGEMENT

+_Bed Management Flow_ is mainly present on the BedManagementModal component. It allows user to modify which beds are in the system, and which beds are assigned to which Patient Monitor. It communicates with many endpoints from Web Gateway for CRUD type operations and assignment

+_Bed Groups Management Flow_ is mainly present on the GroupManagementModal component. It allows user to do CRUD type operations regarding Bed Groups by communicating with many endpoints from the Web Gateway. It also allows the user to assign different beds to patient groups, also by communicating with Web Gateway

### WEBSOCKET COMMUNICATION

+_Realtime data retrieval flow_ is handled on `api/vitalsWorkerWs.ts`, and used through the useMessageSocketHandler hook. It utilices a WebWorker approach to handle all realtime communication with the Realtime Gateway for receiving all updates impacting the current display. This includes new vitals, alerts being turned on/off, or new system wide information like updates on beds, bed groups, patients, sensors, monitors, etc. Some of the logic handling for some of these events is also found on the pages where this communication is used (Home and Details)

## NPM Scripts

`npm i`
Installs all dependencies for the project

`npm run dev`
Runs the app in the development mode.
Open http://localhost:3000 to view it in the browser.

`npm run build`
Builds the app for production to the build folder.

`npm run start`
Starts a production server using the files generated by the build command.

`npm run format`
Formats all code files in the project using Prettier.

`npm run check-format`
Checks whether all code files in the project are formatted correctly using Prettier.

`npm run check-lint`
Checks the code for linting errors using ESLint. The command only checks .js files.

`npm run unit-tests`
Runs unit tests for the app and generates a coverage report. The command runs the tests silently.

`npm run build-storybook`
Builds the storybook project for CMS. Storybook allows the user to open a webpage to check the registered UI components and run tests for those specific components

`npm run storybook`
Runs and opens the storybook webpage to show behavior and UI for CMS Components.

`npm run test-storybook`
Runs stories for storybook components

## TROUBLESHOOTING / COMMON ISSUES

-Problem
App does not load when deployed, and console reports GET {\_next/static URL} net::ERR_ABORTED 404

-Cause
Old file references to static next.js chunks get stuck on a deployed pod, causing an error when referencing them

-Solution
Deleting all pods and recreating them on the environment seems to have fixed the issue before

---

## STRUCTURE

Application code should live mostly on the `/src` folder as usual. The notable exceptions are tests and their mocks (`/__tests__`, `/__mocks__`), images and audio files (`/public`), and middleware code for retrieving Environment variables (`/pages/api`)

Inside the src folder the structure is the following:

`/api`
Code that handles communication with both the web and realtime gateways. Files ending with `Api` handle the data parsing logic, and files starting with `use` are custom hooks for making the requests and handling the responses

`/app`
High-level components code for each webpage inside CMS. Code inside here should be used by one webpage only. Pages that require authentication are inside the `(authenticated)` folder, while free to access webpages are inside their respective folder. Note that the default page file for root url just handles redirection based on current user authentication status

`/components`
Lower-lever components that are available to be reused in different pages throughout CMS. Different subfolders indicate what type of component it is

`/context`
Contexts used throughout CMS to store and retrieve information that is used by multiple pages and components. This information is usually used in multiple different flows

`/hooks`
Hooks that can be used throughout CMS to handle data that has the potential to change rapidly or constantly within a component, depending on various triggers

`/schemas`
Data schemas for structure of data in communication either between CMS and a remote websocket, or within a worker and the core of CMS

`/stories`
Tests written for the storybook components

`/styles`
UI Styles and CSS-like styles to be reused throughout the app for consistent look and feel

`/theme`
Theme for the UI with constants such as colors and sizes for display

`/types`
Types definitions to be used throughout the app

`/utils`
Helper functions for usage throughout the app as needed

Constants for usage throughout the app are stored inside `src/constants.ts`
