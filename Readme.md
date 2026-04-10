# Yandex Agents Week

[April 6-10, 2026](https://shad.yandex.ru/agentsweek)

* Day 1 **Zaytseva Alena**, AI Lead at Yandex Lavka
  * [YT - Lecture 1.1: Intro to AI Agents, LLM](https://www.youtube.com/live/C1OCgbONSAw)
    * [lecture notes (ru)](day1/Intro.ru.md)
    * [slides](day1/Intro.pdf)
    * [notebook 1](day1/Intro1.ipynb)
    * [notebook 2](day1/Intro2.ipynb)
    * [source: Yandex Disk](https://disk.yandex.ru/d/8nYIIjvHglHYYQ)
  * [YT - Lecture 1.2: Tools. MCP](https://www.youtube.com/live/VctYHtCap3o)
    * [lecture notes (ru)](day1/Tools_MCP.ru.md)
    * [slides](day1/Tools_MCP.pdf)
    * [notebook](day1/Tools_MCP.ipynb)
    * [source: Yandex Disk](https://disk.yandex.ru/d/UYvdXggOw8bNtA)
* Day 2 **Кирилл Мищенко**, Head of the ML Development Group at Yandex Browser
  * [YT - Memory and Guardrails in LLM-Powered Agents](https://www.youtube.com/live/iJGh5cBSReo)
    * agenda:
      - purpose of memory and its different types;
      - RAG and learning as a technique for memorizing information, as well as *context* management strategies;
      - importance of Guardrails, the Threat Model, content filters and action limiters,
        tools for Guardrails implementation, and a word on monitoring.
    * [lecture notes (ru)](day2/Memory_Guardrails.ru.md)
    * [slides](day2/Memory_Guardrails.pdf) - [Yandex Disk](https://disk.yandex.ru/d/vWyED4WOXEC07A)
  * [YT - Notebook walk-through](https://www.youtube.com/live/JEFiiM9C_po)
    * agenda:
      - сделаем базовую версию агента, который работает с авиабилетами;
      - добавим долгосрочную и краткосрочную память;
      - реализуем поиск политик и RAG, улучшение ответа через трансформацию запроса методом HyDE;
      - добавим Guardrails;
      - добавим бронирование с подтверждением от оператора.
  * [notebook](day2/Memory_Guardrails.ipynb) - [Yandex Disk](https://disk.yandex.ru/d/LbxlAz6BLxJLUA)
* Day 3 **Софья Проскурина**, платформа внутренних ИИ‑агентов и агенты, оптимизирующие разработку в Яндекс Лавке
  * [YT - AI Agent Workflow. Multi-Agent Systems. Multimodality](https://www.youtube.com/live/_gdXItwkhUE)
    * agenda:
      - поговорим, как агент думает; TAO-цикл, особенности его шагов;
      - архитектуры и подходы Multi-Agent Systems (MAS);
      - обзор мультимодальности.
    * [lecture notes (ru)](day3/Agent.Workflow_MAS_Multimodality.ru.md)
    * [slides](day3/Agent.Workflow_MAS_Multimodality.pdf) - [Yandex Disk](https://disk.yandex.ru/d/us-Ut9B-TCdE0g)
  * [YT - Notebook walk-through](https://www.youtube.com/live/s4BfSnWwAQE)
    * agenda:
      - рассмотрим agent workflow и MAS;
      - TAO-цикл;
      - ReAct-агент;
      - рассмотрим иерархическую мультиагентную систему и добавим в неё критика;
      - сравним разные подходы.
    * [lecture notes (ru)](day4/Agent.Evaluation_Quality.md)
    * [notebook](day3/Agent.Workflow_MAS.ipynb) - [Yandex Disk](https://disk.yandex.ru/d/DtUkSvoi3XzBEQ)
* Day 4 **Сергей Купцов**, развивает агентные решения в Алисе и Умных устройствах
  * [YT - Agent Evaluation: From Metrics to Managed Quality](https://www.youtube.com/live/RqM3G3STkGE)
    * agenda: поговорим о качестве в широком смысле и о понятии Evaluation
    * [slides](day4/Agent.Evaluation_Quality.pdf) - [Yandex Disk](https://disk.yandex.ru/d/BWBgQPk6j4qr_Q)
  * [YT - Notebook walk-through](https://www.youtube.com/live/VYEX17iibkQ)
    * agenda:
      - соберем корзину;
      - определимся с критериями и грейдерами;
      - подключим железного пользователя;
      - сделаем вручную golden-разметку;
      - итеративно улучшим LLM-судью для более высокого качества.
    * [notebook](day4/Evals.ipynb) - [Yandex Disk](https://disk.yandex.ru/d/AqWnepq1PW9WKg)
