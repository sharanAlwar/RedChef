import { useState } from 'react'
import axios from 'axios'

function App() {
  const [ingredients, setIngredients] = useState([])
  const [currentIngredient, setCurrentIngredient] = useState('')
  const [recipe, setRecipe] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAddIngredient = (e) => {
    e.preventDefault()
    if (currentIngredient.trim()) {
      setIngredients([...ingredients, currentIngredient.trim()])
      setCurrentIngredient('')
    }
  }

  const handleRemoveIngredient = (index) => {
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (ingredients.length === 0) {
      setError('Please add at least one ingredient')
      return
    }
    
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('http://localhost:8000/generate-recipe', {
        ingredients: ingredients
      })
      setRecipe(response.data)
    } catch (err) {
      setError('Failed to generate recipe. Please try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-redbull mb-8">
          RedChef
        </h1>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <form onSubmit={handleAddIngredient} className="flex gap-2 mb-4">
            <input
              type="text"
              value={currentIngredient}
              onChange={(e) => setCurrentIngredient(e.target.value)}
              className="input-primary flex-1"
              placeholder="Enter an ingredient"
            />
            <button
              type="submit"
              className="btn-primary whitespace-nowrap"
            >
              Add Ingredient
            </button>
          </form>

          {ingredients.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-gray-300 font-medium">Added Ingredients:</h3>
              <div className="flex flex-wrap gap-2">
                {ingredients.map((ingredient, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 bg-gray-700 px-3 py-1 rounded-full"
                  >
                    <span className="text-gray-300">{ingredient}</span>
                    <button
                      onClick={() => handleRemoveIngredient(index)}
                      className="text-redbull hover:text-redbull-dark"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <button
          onClick={handleSubmit}
          className="btn-primary w-full"
          disabled={loading || ingredients.length === 0}
        >
          {loading ? 'Cooking...' : 'Cook with RedChef'}
        </button>

        {error && (
          <div className="mt-6 p-4 bg-red-900 text-white rounded-lg">
            {error}
          </div>
        )}

        {recipe && (
          <div className="mt-8 space-y-6">
            <h2 className="text-2xl font-bold text-redbull text-center">
              {recipe.cuisine_name}
            </h2>
            
            <div className="bg-gray-800 rounded-lg p-6 space-y-4">
              <h3 className="text-xl font-semibold text-gray-300">Cooking Steps:</h3>
              <ol className="space-y-3">
                {recipe.steps.map((step, index) => (
                  <li key={index} className="text-gray-300">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
