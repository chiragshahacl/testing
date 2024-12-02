<div align="center">
  <br>
  <img alt="tucana" src="https://user-images.githubusercontent.com/108890369/223312587-5c6326cc-5cf8-457d-9bb0-0a90f12190e5.png" height="100">
  <h1>CLOUD TEAM</h1>
  </br>
</div>

# 📄 In-Code Documentation

## 🎯 Objectives

The Cloud team has implemented in-code documentation as a part of the quality activities conforming IEC 62304 standard. With this, the team can maintain the technical documents in parallel to the software development life-cycle; avoiding retroactive documentation. This initiative ensures up-to-date contents per each branch supporting multiple programs with different configurations.

In-code documentation is not limited to a single software or project; it must be applied to all softwares.

The Cloud team's in-code documentation covers the following technical documents:

- Software Configuration Description
- Software Architecture Diagram
- Software Detailed Design
- Test Summary

---

### ⚙️ Software Configuration Description

As the Cloud team is now participating in multiple different programs, it is crucial to document the software configuration in terms of supported features.

The team shall maintain the following software configuration information [HERE](./technical_docs/Configuration.md):

- Program Code
- Project Code
- Software Version # provide the minor version
- List of supported features
- Configurable variables

#### Example:

- Program Code: PRO-177 Macaw
  - if not available, provide the name
- Project Code: PRO-176 Vaquita
- Software Version: Central Hub v2.0
  - provide the {major}.{minor} version
- List of supported features
  - EHR integration with patient query
  - Centralized Authentication system
  - Localization support for German, French, and Dutch
- Configurable variables
  - HOSPITAL_TITLE
  - HOSPITAL_TIMEZONE
  - MAX_NUMBER_BEDS
  - LOCALIZED_LANGUAGE

<b><i>
Please note that this software configuration description shall be updated and confirmed before the release.
</i></b>

---

### 🏛️ Software Architecture Diagram

Once the software requirement specifications are specified, the team will analyze each requirement, then prepare the Software Architecture Diagram.

The Cloud team manager and Cloud technical lead shall draft the architecture of the software. The architecture diagram should be in plantUML with C4 model.

Here are some reference links to plantUML and C4 model:

- [PlantUML](https://plantuml.com/)
- [C4 Model](https://c4model.com/)

#### How to draw the diagram?

Here are the steps to prepare the environment for Visual Studio Code.

1. Install the PlantUML extension (by jebb)
2. Install the Java Runtime Environment (JRE)
3. Create a new file with a .puml extension
4. Paste your PlantUML code into the file
5. Save the file
6. Preview the diagram

---

All diagrams should be stored in `technical_docs/C4_diagram` directory.
`.puml` filenames follow this schema:

`{C4 level}_{Container name}_{Component name}.puml`

#### Example

1. `C2_Patient.puml`
2. `C3_Patient_Bed.puml`

---

#### Design Activity

The initial software architecture diagram will have level 1 (Context) and level 2 (Container) models from the software requirement specifications delivered.

With the initial software architecture diagram, the Cloud technical lead shall draft the detailed design document.

If technical challenges are discovered during software component designing, the stakeholders shall revise the software architecture diagram.

---

### 📑 Software Detailed Design

As decribed above, the initial draft of the software detailed design shall be prepared based on the software architecture diagram.

#### Realization Activity

With the draft software detailed design, JIRA tickets will be created where each JIRA ticket has the corresponding software requirement identifier.

Cloud team engineers shall implement the code according to the description of the JIRA ticket. In parallel to the implementation, all engineers shall record the detailed description on their implementation. Here, level 3 (Components) diagram should be prepared.
Sequence diagrams are also included in this documentation.

Detailed description shall be added to the [`SDD.md`](./technical_docs/SDD.md) document under `technical_docs` directory.

The software detailed design, hereby SDD, has a document structure as following:

---

#### Example

Software Design Description
1. User Interface
   1) Component Design Description
   2) Workflows and Algorithms
   3) Component Interfaces
2. Server
   1) Component Design Description
   2) Workflows and Algorithms
   3) Component Interfaces
3. Infrastructure
4. SOUP Identification
5. Appendix

---


### 🧩 Unit Test & Integration Test

All unit tests and integration test shall be prepared in parallel to the implementation. Cloud engineers are responsible to have 95% code coverage.

The engineer shall map software requirement specifications to each test case while implementing it.

#### Realization Activity

When writing the test, the following information shall be added.

---

1. Software Requirement ID
2. Test Summary (Description)

---