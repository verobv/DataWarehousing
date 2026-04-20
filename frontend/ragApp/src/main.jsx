import ReactDOM from 'react-dom/client'
import App from './App'

const queries = [
  {
    id: 1,
    question: 'Which region has the highest sales?',
  },
  {
    id: 2,
    question: 'How has profit margin changed over time?'
  },
  {
    id: 3,
    question: 'Which product category generates the most revenue?'
  },
  {
    id: 4,
    question: 'Which cities are the top performers?'
  },
  {
    id: 5,
    question: 'How does the West region compare to the East in terms of profit?'
  },
  {
    id: 6,
    question: 'Which products are frequently sold at a discount?'
  },
  {
    id: 7,
    question: 'How has profit margin changed over time?'
  },
  {
    id: 8,
    question: 'Which months show the highest sales? Is there seasonality?'
  },
  {
    id: 9,
    question: 'What sub-categories have the highest profit margins?'
  },
  {
    id: 10,
    question: 'Compare Technology vs. Furniture sales trends.'
  },
]

ReactDOM.createRoot(document.getElementById('root')).render(
  <App queries={queries} />
)