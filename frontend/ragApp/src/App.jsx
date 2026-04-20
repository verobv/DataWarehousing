import { useState } from 'react'

const Query = ({ query, onClick, selected }) => {
  return (
    <li 
      onClick={() => onClick(query)} 
      style={{ 
        cursor: "pointer",
        fontWeight: selected === query.id ? "bold" : "normal", 
        }}>
      {query.question}
    </li>
  )
}

const App = (props) => {
  const [queries] = useState(props.queries)
  const [selected, setSelected] = useState(null)
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const handleQueryClick = async (query) => {
    setSelected(query.id)
    setLoading(true)
    setAnswer('')

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: query.question }),
      })

      const data = await response.json()
      setAnswer(data.answer)
    } catch {
      setAnswer("Error fetching answer")
    }

    setLoading(false)
  }

  return (
    <div>
      <h1>Queries :)</h1>
      <ul>
        {queries.map((query) => (
          <Query key={query.id} query={query} onClick={handleQueryClick} selected={selected}/>
        ))}
      </ul>
      {loading && <p>Loading...</p>}
      {answer && (
        <div>
          <h2>Answer</h2>
          <p>{answer}</p>
        </div>
      )}
    </div>
  )
}

export default App